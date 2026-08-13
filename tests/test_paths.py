from pathlib import Path

from keyplus.storage import paths


def test_linux_path_is_independent_of_working_directory(monkeypatch, tmp_path):
    monkeypatch.setattr(paths.sys, "platform", "linux")
    monkeypatch.setattr(paths.Path, "home", lambda: Path("/home/test"))
    monkeypatch.delenv("XDG_DATA_HOME", raising=False)
    monkeypatch.delenv("SNAP_USER_COMMON", raising=False)
    monkeypatch.chdir(tmp_path)
    assert paths.KeyPlusPaths.for_current_platform().vault_file == Path(
        "/home/test/.local/share/ZFordDev/KeyPlus/keyplus.vault"
    )


def test_snap_path_uses_revision_stable_common_directory(monkeypatch):
    monkeypatch.setattr(paths.sys, "platform", "linux")
    monkeypatch.setenv("SNAP_USER_COMMON", "/home/test/snap/keyplus/common")
    assert paths.KeyPlusPaths.for_current_platform().vault_file == Path(
        "/home/test/snap/keyplus/common/KeyPlus/keyplus.vault"
    )


def test_windows_path_uses_local_appdata(monkeypatch):
    monkeypatch.setattr(paths.sys, "platform", "win32")
    monkeypatch.setenv("LOCALAPPDATA", "C:/Users/Test/AppData/Local")
    assert paths.KeyPlusPaths.for_current_platform().vault_file == Path(
        "C:/Users/Test/AppData/Local/ZFordDev/KeyPlus/keyplus.vault"
    )
