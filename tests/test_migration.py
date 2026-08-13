import base64
import hashlib
import json

import pytest
from cryptography.fernet import Fernet

from keyplus.application.errors import MigrationError
from keyplus.application.service import VaultService
from keyplus.security.kdf import KDFParameters
from keyplus.security.session import VaultSession
from keyplus.storage.migration import find_legacy_pair
from keyplus.storage.paths import KeyPlusPaths
from keyplus.storage.repository import FileVaultRepository


def write_legacy(directory, password="legacy"):
    salt = bytes(range(16))
    verifier = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000)
    (directory / "auth.db").write_bytes(salt + verifier)
    key = base64.urlsafe_b64encode(hashlib.sha256(password.encode()).digest())
    entries = [
        {
            "id": "legacy-id",
            "name": "Legacy",
            "domain": "example.test",
            "password": "old-secret",
            "created": "2026-01-01T00:00:00",
            "updated": "2026-01-02T00:00:00",
        }
    ]
    (directory / "vault.json").write_text(
        Fernet(key).encrypt(json.dumps(entries).encode()).decode()
    )


def make_service(tmp_path):
    target = tmp_path / "new"
    paths = KeyPlusPaths(
        target, target / "keyplus.vault", target / "backups", target / "keyplus.lock"
    )
    return VaultService(
        FileVaultRepository(paths),
        VaultSession(),
        kdf_parameters=KDFParameters(memory_kib=8192, iterations=1),
    ), paths


def test_legacy_migration_preserves_source_files(tmp_path):
    legacy = tmp_path / "legacy"
    legacy.mkdir()
    write_legacy(legacy)
    auth_before = (legacy / "auth.db").read_bytes()
    vault_before = (legacy / "vault.json").read_bytes()
    service, paths = make_service(tmp_path)

    service.migrate_legacy(find_legacy_pair(legacy), "legacy")

    assert service.list_entries()[0].password == "old-secret"
    assert paths.vault_file.exists()
    assert (legacy / "auth.db").read_bytes() == auth_before
    assert (legacy / "vault.json").read_bytes() == vault_before


def test_failed_migration_preserves_source_and_creates_no_target(tmp_path):
    legacy = tmp_path / "legacy"
    legacy.mkdir()
    write_legacy(legacy)
    before = (legacy / "vault.json").read_bytes()
    service, paths = make_service(tmp_path)

    with pytest.raises(MigrationError):
        service.migrate_legacy(find_legacy_pair(legacy), "wrong")

    assert (legacy / "vault.json").read_bytes() == before
    assert not paths.vault_file.exists()
