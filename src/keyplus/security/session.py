"""One interface-independent unlocked-vault session."""

from __future__ import annotations

import time
from collections.abc import Callable

from keyplus.application.errors import VaultLockedError
from keyplus.application.models import VaultDocument


class VaultSession:
    def __init__(
        self,
        *,
        idle_timeout: float = 300.0,
        clock: Callable[[], float] = time.monotonic,
    ):
        self.idle_timeout = idle_timeout
        self._clock = clock
        self._key: bytearray | None = None
        self._document: VaultDocument | None = None
        self._last_activity: float | None = None

    @property
    def unlocked(self) -> bool:
        if self._key is None or self._document is None:
            return False
        if (
            self._last_activity is not None
            and self._clock() - self._last_activity >= self.idle_timeout
        ):
            self.lock()
            return False
        return True

    def open(self, key: bytes, document: VaultDocument) -> None:
        self.lock()
        self._key = bytearray(key)
        self._document = document
        self._last_activity = self._clock()

    def require(self) -> tuple[bytes, VaultDocument]:
        if not self.unlocked:
            raise VaultLockedError("The vault is locked.")
        self._last_activity = self._clock()
        return bytes(self._key), self._document  # type: ignore[arg-type,return-value]

    def replace_document(self, document: VaultDocument) -> None:
        if not self.unlocked:
            raise VaultLockedError("The vault is locked.")
        self._document = document
        self._last_activity = self._clock()

    def lock(self) -> None:
        if self._key is not None:
            for index in range(len(self._key)):
                self._key[index] = 0
        self._key = None
        self._document = None
        self._last_activity = None
