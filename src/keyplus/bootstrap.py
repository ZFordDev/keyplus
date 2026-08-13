"""Composition root shared by source and packaged KeyPlus entry points."""

from keyplus.application.service import VaultService
from keyplus.security.session import VaultSession
from keyplus.storage.paths import KeyPlusPaths
from keyplus.storage.repository import FileVaultRepository


def build_service(*, idle_timeout: float = 300.0) -> VaultService:
    paths = KeyPlusPaths.for_current_platform()
    return VaultService(
        FileVaultRepository(paths), VaultSession(idle_timeout=idle_timeout)
    )
