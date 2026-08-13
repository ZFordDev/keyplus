"""Atomic encrypted-vault file persistence."""

from __future__ import annotations

import hashlib
import os
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from keyplus.application.errors import (
    BackupError,
    VaultBusyError,
    VaultNotInitializedError,
    VaultReadError,
    VaultWriteError,
)

from .format import VaultEnvelope
from .locking import FileLock
from .paths import KeyPlusPaths


class FileVaultRepository:
    def __init__(self, paths: KeyPlusPaths):
        self.paths = paths

    def exists(self) -> bool:
        return self.paths.vault_file.is_file()

    def read(self) -> VaultEnvelope:
        if not self.exists():
            raise VaultNotInitializedError("No KeyPlus vault has been initialized.")
        try:
            return VaultEnvelope.from_bytes(self.paths.vault_file.read_bytes())
        except VaultNotInitializedError:
            raise
        except OSError as exc:
            raise VaultReadError("KeyPlus could not read the vault file.") from exc

    def read_external(self, path: Path) -> VaultEnvelope:
        try:
            return VaultEnvelope.from_bytes(path.read_bytes())
        except OSError as exc:
            raise VaultReadError(
                "KeyPlus could not read the selected vault backup."
            ) from exc

    def revision(self) -> str | None:
        if not self.exists():
            return None
        try:
            return hashlib.sha256(self.paths.vault_file.read_bytes()).hexdigest()
        except OSError as exc:
            raise VaultReadError("KeyPlus could not read the vault file.") from exc

    def write(
        self,
        envelope: VaultEnvelope,
        *,
        preserve_previous: bool = True,
        expected_revision: str | None = None,
    ) -> str:
        raw = envelope.to_bytes()
        directory = self.paths.data_dir
        temporary: Path | None = None
        try:
            directory.mkdir(parents=True, exist_ok=True, mode=0o700)
            if os.name != "nt":
                os.chmod(directory, 0o700)
            with FileLock(self.paths.lock_file):
                current_revision = self.revision()
                if (
                    expected_revision is not None
                    and current_revision != expected_revision
                ):
                    raise VaultWriteError(
                        "The vault changed in another KeyPlus process. Lock and reopen it before retrying."
                    )
                if preserve_previous and self.paths.vault_file.exists():
                    self._write_last_good_backup()
                fd, name = tempfile.mkstemp(
                    prefix=".keyplus-", suffix=".tmp", dir=directory
                )
                temporary = Path(name)
                try:
                    if os.name != "nt":
                        os.fchmod(fd, 0o600)
                    with os.fdopen(fd, "wb") as stream:
                        stream.write(raw)
                        stream.flush()
                        os.fsync(stream.fileno())
                    VaultEnvelope.from_bytes(temporary.read_bytes())
                    os.replace(temporary, self.paths.vault_file)
                    temporary = None
                    if os.name != "nt":
                        os.chmod(self.paths.vault_file, 0o600)
                        directory_fd = os.open(directory, os.O_RDONLY)
                        try:
                            os.fsync(directory_fd)
                        finally:
                            os.close(directory_fd)
                    return hashlib.sha256(raw).hexdigest()
                except Exception:
                    if temporary and temporary.exists():
                        temporary.unlink(missing_ok=True)
                    raise
        except (VaultWriteError, VaultBusyError, BackupError):
            raise
        except Exception as exc:
            raise VaultWriteError(
                "KeyPlus could not safely write the vault file."
            ) from exc

    def create_backup(self) -> Path:
        if not self.exists():
            raise VaultNotInitializedError("No KeyPlus vault has been initialized.")
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        destination = self.paths.backup_dir / f"keyplus-{timestamp}.vault"
        counter = 1
        while destination.exists():
            destination = self.paths.backup_dir / f"keyplus-{timestamp}-{counter}.vault"
            counter += 1
        try:
            self.paths.backup_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
            with FileLock(self.paths.lock_file):
                # Validate under the same lock used for the copy.
                self.read()
                shutil.copyfile(self.paths.vault_file, destination)
            if os.name != "nt":
                os.chmod(self.paths.backup_dir, 0o700)
                os.chmod(destination, 0o600)
            return destination
        except OSError as exc:
            raise BackupError(
                "KeyPlus could not create an encrypted vault backup."
            ) from exc

    def _write_last_good_backup(self) -> None:
        # Only preserve a structurally valid envelope.
        self.read()
        self.paths.backup_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        destination = self.paths.backup_dir / "last-good.vault"
        temp = self.paths.backup_dir / ".last-good.tmp"
        try:
            shutil.copyfile(self.paths.vault_file, temp)
            if os.name != "nt":
                os.chmod(temp, 0o600)
            os.replace(temp, destination)
        finally:
            temp.unlink(missing_ok=True)
