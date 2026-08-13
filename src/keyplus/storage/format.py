"""Versioned KeyPlus encrypted-vault envelope."""

from __future__ import annotations

import base64
import json
import os
from dataclasses import dataclass
from typing import Any

from keyplus.application.errors import CorruptVaultError, UnsupportedVaultVersionError
from keyplus.application.models import VaultDocument
from keyplus.security import cipher
from keyplus.security.kdf import DEFAULT_KDF_PARAMETERS, KDFParameters, derive_key

FORMAT_NAME = "keyplus-vault"
FORMAT_VERSION = 1
KDF_NAME = "argon2id"
CIPHER_NAME = "aes-256-gcm"


def _b64(value: bytes) -> str:
    return base64.b64encode(value).decode("ascii")


def _decode(value: Any, label: str) -> bytes:
    try:
        return base64.b64decode(str(value), validate=True)
    except Exception as exc:
        raise CorruptVaultError(f"The vault {label} is invalid.") from exc


@dataclass(frozen=True)
class VaultEnvelope:
    salt: bytes
    parameters: KDFParameters
    nonce: bytes
    ciphertext: bytes

    @staticmethod
    def associated_data(parameters: KDFParameters) -> bytes:
        header = {
            "format": FORMAT_NAME,
            "version": FORMAT_VERSION,
            "kdf": {
                "name": KDF_NAME,
                "memory_kib": parameters.memory_kib,
                "iterations": parameters.iterations,
                "parallelism": parameters.parallelism,
                "length": parameters.length,
            },
            "cipher": {"name": CIPHER_NAME},
        }
        return json.dumps(header, sort_keys=True, separators=(",", ":")).encode("utf-8")

    def to_bytes(self) -> bytes:
        value = json.loads(self.associated_data(self.parameters))
        value["kdf"]["salt"] = _b64(self.salt)
        value["cipher"]["nonce"] = _b64(self.nonce)
        value["ciphertext"] = _b64(self.ciphertext)
        return (json.dumps(value, sort_keys=True, indent=2) + "\n").encode("utf-8")

    @classmethod
    def from_bytes(cls, raw: bytes) -> VaultEnvelope:
        try:
            value = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise CorruptVaultError("The vault envelope is not valid JSON.") from exc
        if not isinstance(value, dict) or value.get("format") != FORMAT_NAME:
            raise CorruptVaultError("This file is not a KeyPlus vault.")
        if value.get("version") != FORMAT_VERSION:
            raise UnsupportedVaultVersionError(
                f"Vault format version {value.get('version')!r} is not supported."
            )
        try:
            kdf = value["kdf"]
            cipher_value = value["cipher"]
            if kdf["name"] != KDF_NAME or cipher_value["name"] != CIPHER_NAME:
                raise UnsupportedVaultVersionError(
                    "The vault uses an unsupported cryptographic profile."
                )
            parameters = KDFParameters(
                memory_kib=int(kdf["memory_kib"]),
                iterations=int(kdf["iterations"]),
                parallelism=int(kdf["parallelism"]),
                length=int(kdf["length"]),
            ).validate()
            return cls(
                salt=_decode(kdf["salt"], "salt"),
                parameters=parameters,
                nonce=_decode(cipher_value["nonce"], "nonce"),
                ciphertext=_decode(value["ciphertext"], "ciphertext"),
            )
        except UnsupportedVaultVersionError:
            raise
        except CorruptVaultError:
            raise
        except (KeyError, TypeError, ValueError) as exc:
            raise CorruptVaultError(
                "The vault envelope is incomplete or invalid."
            ) from exc


def create_envelope(
    document: VaultDocument,
    password: str,
    parameters: KDFParameters = DEFAULT_KDF_PARAMETERS,
) -> tuple[VaultEnvelope, bytes]:
    salt = os.urandom(16)
    key = derive_key(password, salt, parameters)
    return encrypt_document(document, key, salt, parameters), key


def encrypt_document(
    document: VaultDocument, key: bytes, salt: bytes, parameters: KDFParameters
) -> VaultEnvelope:
    plaintext = json.dumps(
        document.to_dict(), sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    aad = VaultEnvelope.associated_data(parameters)
    nonce, ciphertext = cipher.encrypt(plaintext, key, aad)
    return VaultEnvelope(salt, parameters, nonce, ciphertext)


def unlock_envelope(
    envelope: VaultEnvelope, password: str
) -> tuple[bytes, VaultDocument]:
    key = derive_key(password, envelope.salt, envelope.parameters)
    plaintext = cipher.decrypt(
        envelope.ciphertext,
        envelope.nonce,
        key,
        envelope.associated_data(envelope.parameters),
    )
    try:
        value = json.loads(plaintext.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CorruptVaultError("The decrypted vault payload is invalid.") from exc
    return key, VaultDocument.from_dict(value)
