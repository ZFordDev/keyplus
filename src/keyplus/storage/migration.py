"""Read-only import of verified KeyPlus 0.2 working-directory vault pairs."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from cryptography.fernet import Fernet, InvalidToken

from keyplus.application.errors import MigrationError
from keyplus.application.models import VaultDocument, VaultEntry


@dataclass(frozen=True)
class LegacyVaultPair:
    directory: Path
    auth_file: Path
    vault_file: Path


def find_legacy_pair(directory: Path) -> LegacyVaultPair | None:
    auth_file = directory / "auth.db"
    vault_file = directory / "vault.json"
    if auth_file.is_file() and vault_file.is_file():
        return LegacyVaultPair(
            directory.resolve(), auth_file.resolve(), vault_file.resolve()
        )
    return None


def discover_legacy_pairs(candidates: list[Path]) -> list[LegacyVaultPair]:
    found: dict[Path, LegacyVaultPair] = {}
    for candidate in candidates:
        pair = find_legacy_pair(candidate)
        if pair:
            found[pair.directory] = pair
    return list(found.values())


def read_legacy_vault(pair: LegacyVaultPair, password: str) -> VaultDocument:
    try:
        auth_bytes = pair.auth_file.read_bytes()
        ciphertext = pair.vault_file.read_text(encoding="utf-8")
    except OSError as exc:
        raise MigrationError(
            "KeyPlus could not read the selected legacy vault files."
        ) from exc
    if len(auth_bytes) != 48:
        raise MigrationError("The selected legacy authentication file is invalid.")
    salt, saved_hash = auth_bytes[:16], auth_bytes[16:]
    candidate = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
    if not hmac.compare_digest(candidate, saved_hash):
        raise MigrationError("The legacy master password is incorrect.")
    key = base64.urlsafe_b64encode(hashlib.sha256(password.encode("utf-8")).digest())
    try:
        raw_entries = json.loads(
            Fernet(key).decrypt(ciphertext.encode("utf-8")).decode("utf-8")
        )
    except (InvalidToken, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise MigrationError("The legacy vault is damaged or incompatible.") from exc
    if not isinstance(raw_entries, list):
        raise MigrationError("The legacy vault payload is invalid.")
    entries = [_convert_entry(value) for value in raw_entries]
    timestamps = [entry.created_at for entry in entries if entry.created_at]
    created = min(timestamps) if timestamps else datetime.now(timezone.utc).isoformat()
    updated_values = [entry.updated_at for entry in entries if entry.updated_at]
    updated = max(updated_values) if updated_values else created
    return VaultDocument(created, updated, entries)


def _convert_entry(value: Any) -> VaultEntry:
    try:
        entry_id = str(value["id"])
        name = str(value["name"]).strip()
        domain = str(value["domain"]).strip()
        password = str(value["password"])
        created = str(value["created"])
        updated = str(value["updated"])
        if not all((entry_id, name, domain, password, created, updated)):
            raise ValueError("empty field")
        return VaultEntry(entry_id, name, domain, password, created, updated)
    except (KeyError, TypeError, ValueError) as exc:
        raise MigrationError("The legacy vault contains an invalid entry.") from exc
