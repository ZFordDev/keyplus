import json
import os

import pytest

from keyplus.application.errors import (
    CorruptVaultError,
    RestoreError,
    UnlockFailedError,
    UnsupportedVaultVersionError,
    VaultLockedError,
    VaultWriteError,
)
from keyplus.application.models import EntryChanges, EntryDraft
from keyplus.application.service import VaultService
from keyplus.security.kdf import KDFParameters
from keyplus.security.session import VaultSession
from keyplus.storage.paths import KeyPlusPaths
from keyplus.storage.repository import FileVaultRepository

TEST_KDF = KDFParameters(memory_kib=8192, iterations=1, parallelism=1)


def make_service(tmp_path, *, clock=lambda: 0.0):
    paths = KeyPlusPaths(
        tmp_path,
        tmp_path / "keyplus.vault",
        tmp_path / "backups",
        tmp_path / "keyplus.lock",
    )
    service = VaultService(
        FileVaultRepository(paths),
        VaultSession(idle_timeout=10, clock=clock),
        kdf_parameters=TEST_KDF,
        now=lambda: "2026-08-13T00:00:00+00:00",
    )
    return service, paths


def test_create_open_and_crud_round_trip(tmp_path):
    service, paths = make_service(tmp_path)
    service.initialize("correct horse")
    created = service.add_entry(EntryDraft("GitHub", "github.com", "secret"))
    service.update_entry(created.id, EntryChanges(password="new-secret"))
    service.lock()

    reopened, _ = make_service(tmp_path)
    reopened.unlock("correct horse")
    entry = reopened.get_entry(created.id)
    assert entry.password == "new-secret"
    assert len(reopened.list_entries()) == 1

    reopened.delete_entry(created.id)
    assert reopened.list_entries() == ()
    assert paths.vault_file.exists()
    assert (paths.backup_dir / "last-good.vault").exists()


def test_wrong_password_does_not_unlock(tmp_path):
    service, _ = make_service(tmp_path)
    service.initialize("correct")
    service.lock()
    with pytest.raises(UnlockFailedError):
        service.unlock("wrong")
    assert not service.unlocked


def test_corrupt_envelope_is_not_replaced(tmp_path):
    service, paths = make_service(tmp_path)
    service.initialize("correct")
    original = b"not json"
    paths.vault_file.write_bytes(original)
    service.lock()
    with pytest.raises(CorruptVaultError):
        service.unlock("correct")
    assert paths.vault_file.read_bytes() == original


def test_session_expiry_invalidates_state(tmp_path):
    now = [0.0]
    service, _ = make_service(tmp_path, clock=lambda: now[0])
    service.initialize("correct")
    now[0] = 11.0
    with pytest.raises(VaultLockedError):
        service.list_entries()
    assert not service.unlocked


def test_change_password_is_atomic_from_user_view(tmp_path):
    service, paths = make_service(tmp_path)
    service.initialize("old")
    service.add_entry(EntryDraft("Site", "site.test", "password"))
    service.change_master_password("old", "new")
    previous = paths.backup_dir / "last-good.vault"
    assert previous.exists()
    service.lock()
    with pytest.raises(UnlockFailedError):
        service.unlock("old")
    service.unlock("new")
    assert service.list_entries()[0].name == "Site"

    service.restore_backup(previous, "old")
    service.lock()
    service.unlock("old")
    assert service.list_entries()[0].name == "Site"


def test_wrong_current_password_preserves_vault_and_session(tmp_path):
    service, paths = make_service(tmp_path)
    service.initialize("old")
    before = paths.vault_file.read_bytes()

    with pytest.raises(UnlockFailedError):
        service.change_master_password("wrong", "new")

    assert paths.vault_file.read_bytes() == before
    assert service.unlocked
    service.lock()
    service.unlock("old")


def test_password_change_requires_unlocked_session(tmp_path):
    service, _ = make_service(tmp_path)
    service.initialize("old")
    service.lock()

    with pytest.raises(VaultLockedError):
        service.change_master_password("old", "new")


@pytest.mark.skipif(os.name == "nt", reason="POSIX permission assertion")
def test_repository_applies_private_permissions(tmp_path):
    service, paths = make_service(tmp_path)
    service.initialize("correct")
    assert paths.data_dir.stat().st_mode & 0o777 == 0o700
    assert paths.vault_file.stat().st_mode & 0o777 == 0o600


def test_envelope_has_explicit_format_metadata(tmp_path):
    service, paths = make_service(tmp_path)
    service.initialize("correct")
    envelope = json.loads(paths.vault_file.read_text())
    assert envelope["format"] == "keyplus-vault"
    assert envelope["version"] == 1
    assert envelope["kdf"]["name"] == "argon2id"
    assert envelope["cipher"]["name"] == "aes-256-gcm"


def test_unsupported_format_version_is_rejected(tmp_path):
    service, paths = make_service(tmp_path)
    service.initialize("correct")
    service.lock()
    envelope = json.loads(paths.vault_file.read_text())
    envelope["version"] = 99
    paths.vault_file.write_text(json.dumps(envelope))

    with pytest.raises(UnsupportedVaultVersionError):
        service.unlock("correct")


def test_authenticated_ciphertext_tampering_is_rejected(tmp_path):
    service, paths = make_service(tmp_path)
    service.initialize("correct")
    service.lock()
    envelope = json.loads(paths.vault_file.read_text())
    ciphertext = envelope["ciphertext"]
    envelope["ciphertext"] = ("A" if ciphertext[0] != "A" else "B") + ciphertext[1:]
    paths.vault_file.write_text(json.dumps(envelope))

    with pytest.raises(UnlockFailedError):
        service.unlock("correct")


def test_stale_service_cannot_overwrite_newer_data(tmp_path):
    first, _ = make_service(tmp_path)
    first.initialize("correct")
    second, _ = make_service(tmp_path)
    second.unlock("correct")
    first.add_entry(EntryDraft("First", "first.test", "one"))
    with pytest.raises(VaultWriteError, match="changed in another"):
        second.add_entry(EntryDraft("Second", "second.test", "two"))


def test_replace_failure_preserves_existing_vault(tmp_path, monkeypatch):
    service, paths = make_service(tmp_path)
    service.initialize("correct")
    before = paths.vault_file.read_bytes()

    def fail_replace(_source, _destination):
        raise OSError("simulated replace failure")

    monkeypatch.setattr("keyplus.storage.repository.os.replace", fail_replace)
    with pytest.raises(VaultWriteError):
        service.add_entry(EntryDraft("Site", "site.test", "secret"))
    assert paths.vault_file.read_bytes() == before


def test_encrypted_backup_can_be_restored(tmp_path):
    service, _ = make_service(tmp_path)
    service.initialize("correct")
    original = service.add_entry(EntryDraft("Original", "one.test", "one"))
    backup = service.create_backup()
    service.add_entry(EntryDraft("Later", "two.test", "two"))

    service.restore_backup(backup, "correct")

    assert [entry.id for entry in service.list_entries()] == [original.id]


def test_failed_restore_preserves_active_vault(tmp_path):
    service, paths = make_service(tmp_path)
    service.initialize("correct")
    service.add_entry(EntryDraft("Current", "current.test", "secret"))
    before = paths.vault_file.read_bytes()
    invalid = tmp_path / "invalid.vault"
    invalid.write_text("not a vault")

    with pytest.raises(RestoreError, match="validate and restore"):
        service.restore_backup(invalid, "correct")

    assert paths.vault_file.read_bytes() == before
    assert service.list_entries()[0].name == "Current"


def test_wrong_backup_password_preserves_active_vault(tmp_path):
    service, paths = make_service(tmp_path)
    service.initialize("correct")
    backup = service.create_backup()
    before = paths.vault_file.read_bytes()

    with pytest.raises(RestoreError):
        service.restore_backup(backup, "wrong")

    assert paths.vault_file.read_bytes() == before
    assert service.unlocked


def test_unsupported_backup_version_preserves_active_vault(tmp_path):
    service, paths = make_service(tmp_path)
    service.initialize("correct")
    backup = service.create_backup()
    value = json.loads(backup.read_text())
    value["version"] = 99
    backup.write_text(json.dumps(value))
    before = paths.vault_file.read_bytes()

    with pytest.raises(RestoreError):
        service.restore_backup(backup, "correct")

    assert paths.vault_file.read_bytes() == before


def test_restore_write_failure_preserves_active_vault(tmp_path, monkeypatch):
    service, paths = make_service(tmp_path)
    service.initialize("correct")
    backup = service.create_backup()
    service.add_entry(EntryDraft("Current", "current.test", "secret"))
    before = paths.vault_file.read_bytes()
    real_replace = os.replace

    def fail_active_replace(source, destination):
        if destination == paths.vault_file:
            raise OSError("simulated restore failure")
        return real_replace(source, destination)

    monkeypatch.setattr("keyplus.storage.repository.os.replace", fail_active_replace)
    with pytest.raises(RestoreError):
        service.restore_backup(backup, "correct")

    assert paths.vault_file.read_bytes() == before
    assert service.list_entries()[0].name == "Current"


def test_backup_names_do_not_collide_and_inventory_is_listed(tmp_path):
    service, _ = make_service(tmp_path)
    service.initialize("correct")
    first = service.create_backup()
    second = service.create_backup()

    assert first != second
    assert set(service.list_backups()) >= {first, second}


def test_corrupt_last_good_is_replaced_from_valid_active_vault(tmp_path):
    service, paths = make_service(tmp_path)
    service.initialize("correct")
    paths.backup_dir.mkdir()
    last_good = paths.backup_dir / "last-good.vault"
    last_good.write_text("damaged")

    service.add_entry(EntryDraft("New", "new.test", "secret"))

    service.restore_backup(last_good, "correct")
    assert service.list_entries() == ()
