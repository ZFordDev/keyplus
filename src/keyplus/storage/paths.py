"""Deterministic platform-specific KeyPlus paths."""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class KeyPlusPaths:
    data_dir: Path
    vault_file: Path
    backup_dir: Path
    lock_file: Path

    @classmethod
    def for_current_platform(cls) -> KeyPlusPaths:
        home = Path.home()
        if sys.platform == "win32":
            base = (
                Path(os.environ.get("LOCALAPPDATA", home / "AppData" / "Local"))
                / "ZFordDev"
                / "KeyPlus"
            )
        else:
            snap_common = os.environ.get("SNAP_USER_COMMON", "").strip()
            if snap_common:
                base = Path(snap_common) / "KeyPlus"
            else:
                xdg_data = os.environ.get("XDG_DATA_HOME", "").strip()
                root = Path(xdg_data) if xdg_data else home / ".local" / "share"
                base = root / "ZFordDev" / "KeyPlus"
        return cls(
            base, base / "keyplus.vault", base / "backups", base / "keyplus.lock"
        )
