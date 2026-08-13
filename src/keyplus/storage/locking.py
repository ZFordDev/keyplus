"""Small cross-platform advisory file lock used for vault transactions."""

from __future__ import annotations

import os
import time
from pathlib import Path

from keyplus.application.errors import VaultBusyError, VaultWriteError


class FileLock:
    def __init__(self, path: Path, *, timeout: float = 2.0):
        self.path = path
        self.timeout = timeout
        self._file = None

    def __enter__(self):
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            self._file = open(self.path, "a+b")
            if os.name != "nt":
                os.chmod(self.path, 0o600)
        except OSError as exc:
            raise VaultWriteError(
                "KeyPlus could not create its vault lock file."
            ) from exc

        deadline = time.monotonic() + self.timeout
        while True:
            try:
                self._acquire()
                return self
            except (BlockingIOError, OSError):
                if time.monotonic() >= deadline:
                    self.__exit__(None, None, None)
                    raise VaultBusyError(
                        "The vault is in use by another KeyPlus process."
                    )
                time.sleep(0.05)

    def _acquire(self) -> None:
        if os.name == "nt":
            import msvcrt

            self._file.seek(0)
            if self._file.read(1) == b"":
                self._file.write(b"0")
                self._file.flush()
            self._file.seek(0)
            msvcrt.locking(self._file.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl

            fcntl.flock(self._file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)

    def __exit__(self, exc_type, exc, traceback):
        if self._file is None:
            return
        try:
            if os.name == "nt":
                import msvcrt

                self._file.seek(0)
                msvcrt.locking(self._file.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl

                fcntl.flock(self._file.fileno(), fcntl.LOCK_UN)
        except OSError:
            pass
        finally:
            self._file.close()
            self._file = None
