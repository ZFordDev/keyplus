"""Interface-neutral errors raised by the KeyPlus application core."""


class KeyPlusError(Exception):
    """Base class for errors that presentation layers may handle."""


class VaultNotInitializedError(KeyPlusError):
    pass


class VaultAlreadyInitializedError(KeyPlusError):
    pass


class VaultLockedError(KeyPlusError):
    pass


class UnlockFailedError(KeyPlusError):
    pass


class CorruptVaultError(KeyPlusError):
    pass


class UnsupportedVaultVersionError(KeyPlusError):
    pass


class InvalidKDFParametersError(KeyPlusError):
    pass


class VaultBusyError(KeyPlusError):
    pass


class VaultReadError(KeyPlusError):
    pass


class VaultWriteError(KeyPlusError):
    pass


class BackupError(KeyPlusError):
    pass


class RestoreError(KeyPlusError):
    pass


class MigrationError(KeyPlusError):
    pass


class EntryNotFoundError(KeyPlusError):
    pass


class AmbiguousEntryError(KeyPlusError):
    pass


class ValidationError(KeyPlusError, ValueError):
    pass
