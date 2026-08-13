"""Shared KeyPlus application service used by every presentation layer."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import replace
from pathlib import Path

from keyplus.security.kdf import DEFAULT_KDF_PARAMETERS, KDFParameters
from keyplus.security.session import VaultSession
from keyplus.storage.format import create_envelope, encrypt_document, unlock_envelope
from keyplus.storage.migration import LegacyVaultPair, read_legacy_vault
from keyplus.storage.repository import FileVaultRepository

from .errors import (
    EntryNotFoundError,
    KeyPlusError,
    MigrationError,
    RestoreError,
    VaultAlreadyInitializedError,
)
from .models import EntryChanges, EntryDraft, VaultDocument, VaultEntry, utc_now


class VaultService:
    def __init__(
        self,
        repository: FileVaultRepository,
        session: VaultSession,
        *,
        kdf_parameters: KDFParameters = DEFAULT_KDF_PARAMETERS,
        now: Callable[[], str] = utc_now,
    ):
        self.repository = repository
        self.session = session
        self.kdf_parameters = kdf_parameters
        self._now = now
        self._salt: bytes | None = None
        self._parameters: KDFParameters | None = None
        self._revision: str | None = None

    @property
    def initialized(self) -> bool:
        return self.repository.exists()

    @property
    def unlocked(self) -> bool:
        return self.session.unlocked

    def initialize(self, password: str) -> None:
        if self.initialized:
            raise VaultAlreadyInitializedError("A KeyPlus vault already exists.")
        document = VaultDocument.empty(now=self._now())
        envelope, key = create_envelope(document, password, self.kdf_parameters)
        self._revision = self.repository.write(envelope, preserve_previous=False)
        self._salt, self._parameters = envelope.salt, envelope.parameters
        self._revision = self.repository.revision()
        self.session.open(key, document)

    def unlock(self, password: str) -> None:
        envelope = self.repository.read()
        key, document = unlock_envelope(envelope, password)
        self._salt, self._parameters = envelope.salt, envelope.parameters
        self._revision = self.repository.revision()
        self.session.open(key, document)

    def lock(self) -> None:
        self.session.lock()
        self._salt = None
        self._parameters = None
        self._revision = None

    def list_entries(self) -> tuple[VaultEntry, ...]:
        _, document = self.session.require()
        return tuple(document.entries)

    def get_entry(self, entry_id: str) -> VaultEntry:
        _, document = self.session.require()
        for entry in document.entries:
            if entry.id == entry_id:
                return entry
        raise EntryNotFoundError(f"No vault entry matches ID '{entry_id}'.")

    def add_entry(self, draft: EntryDraft) -> VaultEntry:
        key, document = self.session.require()
        now = self._now()
        entry = VaultEntry.create(draft, now=now)
        updated = replace(document, updated_at=now, entries=[*document.entries, entry])
        self._persist(updated, key)
        return entry

    def update_entry(self, entry_id: str, changes: EntryChanges) -> VaultEntry:
        key, document = self.session.require()
        now = self._now()
        updated_entry: VaultEntry | None = None
        entries: list[VaultEntry] = []
        for entry in document.entries:
            if entry.id == entry_id:
                updated_entry = changes.apply(entry, now)
                entries.append(updated_entry)
            else:
                entries.append(entry)
        if updated_entry is None:
            raise EntryNotFoundError(f"No vault entry matches ID '{entry_id}'.")
        self._persist(replace(document, updated_at=now, entries=entries), key)
        return updated_entry

    def delete_entry(self, entry_id: str) -> None:
        key, document = self.session.require()
        entries = [entry for entry in document.entries if entry.id != entry_id]
        if len(entries) == len(document.entries):
            raise EntryNotFoundError(f"No vault entry matches ID '{entry_id}'.")
        self._persist(replace(document, updated_at=self._now(), entries=entries), key)

    def change_master_password(self, current_password: str, new_password: str) -> None:
        # Re-authenticate from disk rather than trusting only an unlocked UI.
        envelope = self.repository.read()
        disk_revision = self.repository.revision()
        _, document = unlock_envelope(envelope, current_password)
        replacement, key = create_envelope(document, new_password, self.kdf_parameters)
        self._revision = self.repository.write(
            replacement, expected_revision=disk_revision
        )
        self._salt, self._parameters = replacement.salt, replacement.parameters
        self.session.open(key, document)

    def create_backup(self) -> Path:
        self.session.require()
        return self.repository.create_backup()

    def restore_backup(self, backup: Path, password: str) -> None:
        try:
            envelope = self.repository.read_external(backup)
            key, document = unlock_envelope(envelope, password)
            current_revision = self.repository.revision()
            self._revision = self.repository.write(
                envelope,
                preserve_previous=self.repository.exists(),
                expected_revision=current_revision,
            )
        except KeyPlusError as exc:
            raise RestoreError(
                "KeyPlus could not validate and restore the selected encrypted backup."
            ) from exc
        self._salt, self._parameters = envelope.salt, envelope.parameters
        self.session.open(key, document)

    def migrate_legacy(self, pair: LegacyVaultPair, password: str) -> None:
        if self.initialized:
            raise MigrationError(
                "A KeyPlus 0.3 vault already exists; migration was not started."
            )
        document = read_legacy_vault(pair, password)
        envelope, _ = create_envelope(document, password, self.kdf_parameters)
        # The legacy files remain authoritative; repository writes never modify them.
        installed_new_vault = False
        try:
            self._revision = self.repository.write(envelope, preserve_previous=False)
            installed_new_vault = True
            # Prove the installed file can be opened before reporting success.
            installed = self.repository.read()
            check_key, check_document = unlock_envelope(installed, password)
            if check_document.to_dict() != document.to_dict():
                raise MigrationError("The migrated vault did not pass validation.")
        except Exception as exc:
            if installed_new_vault:
                self.repository.paths.vault_file.unlink(missing_ok=True)
            self._revision = None
            if isinstance(exc, MigrationError):
                raise
            raise MigrationError(
                "KeyPlus could not install and validate the migrated vault. The legacy files were preserved."
            ) from exc
        self._salt, self._parameters = installed.salt, installed.parameters
        self.session.open(check_key, check_document)

    def _persist(self, document: VaultDocument, key: bytes) -> None:
        if self._salt is None or self._parameters is None:
            raise RuntimeError("Unlocked session is missing vault format metadata.")
        envelope = encrypt_document(document, key, self._salt, self._parameters)
        self._revision = self.repository.write(
            envelope, expected_revision=self._revision
        )
        self.session.replace_document(document)
