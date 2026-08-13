"""Authenticated encryption using the cryptography library's AES-GCM API."""

import os

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from keyplus.application.errors import UnlockFailedError

NONCE_BYTES = 12


def encrypt(
    plaintext: bytes, key: bytes, associated_data: bytes
) -> tuple[bytes, bytes]:
    nonce = os.urandom(NONCE_BYTES)
    return nonce, AESGCM(key).encrypt(nonce, plaintext, associated_data)


def decrypt(
    ciphertext: bytes, nonce: bytes, key: bytes, associated_data: bytes
) -> bytes:
    if len(nonce) != NONCE_BYTES:
        raise UnlockFailedError("The vault could not be unlocked.")
    try:
        return AESGCM(key).decrypt(nonce, ciphertext, associated_data)
    except InvalidTag as exc:
        raise UnlockFailedError(
            "The vault could not be unlocked. The password may be incorrect, or the vault may be damaged."
        ) from exc
