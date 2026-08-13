"""
if you know my development style you know i like to keep logic and UI separate.
this is the engine core that handles the actual deployment of the payload and environment setup.
it is called from the installer.py GUI script.
in future i plan to add a CLI interface to this engine so that it can be used in automated deployment scenarios
without the GUI to keep the flow of what keyplus is, a cli first gui second application.
"""

import ctypes
import hashlib
import json
import os
import shutil
import sys
import winreg
from pathlib import Path


class InstallerEngine:
    def __init__(self, vendor_name="ZFordDev", app_name="KeyPlus"):
        self.vendor_name = vendor_name
        self.app_name = app_name
        self.default_dir = (
            Path(os.environ.get("LOCALAPPDATA", "C:\\"))
            / self.vendor_name
            / self.app_name
        )

    def get_payload_source(self):
        """Resolves PyInstaller multi-file extraction paths vs local source contexts."""
        if hasattr(sys, "_MEIPASS"):
            return Path(sys._MEIPASS) / "dist_payload"
        return Path(__file__).parent / "dist_payload"

    def compute_file_checksum(self, file_path):
        """Compute SHA256 checksum for a single file."""
        h = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()

    def read_checksums(self, payload_src):
        """Reads expected checksums from a checksums.json file in the payload source."""
        checksums_file = payload_src / "checksums.json"
        if not checksums_file.exists():
            return {}
        try:
            with open(checksums_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError):
            return {}

    def ensure_mock_payload_exists(self, payload_src):
        """Fallback check for local development scaffolding."""
        if not payload_src.exists():
            payload_src.mkdir(parents=True, exist_ok=True)
            exe_file = payload_src / "keyplus.exe"
            with open(exe_file, "wb") as f:
                f.write(b"Mock Executable Data")

            # produce a simple checksums.json for local dev
            cs = {"keyplus.exe": self.compute_file_checksum(exe_file)}
            with open(payload_src / "checksums.json", "w", encoding="utf-8") as f:
                json.dump(cs, f)

    def execute_deployment(
        self, target_directory, add_to_path=True, create_shortcut=True
    ):
        """Orchestrates the transactional sequence of file and environment setups."""
        target_dir = Path(target_directory)
        payload_src = self.get_payload_source()

        # Guard for development setup validation
        self.ensure_mock_payload_exists(payload_src)

        # 1. Clear out historical instances and extract binary payload
        if target_dir.exists():
            shutil.rmtree(target_dir)
        shutil.copytree(payload_src, target_dir)

        exe_path = target_dir / "keyplus.exe"
        gui_exe_path = target_dir / "gui" / "keyplus-gui.exe"

        # 1.5 Verify delivered payload against checksums
        expected = self.read_checksums(payload_src)
        for relative_name, expected_hash in expected.items():
            delivered = target_dir / Path(relative_name)
            if (
                not delivered.is_file()
                or self.compute_file_checksum(delivered).lower()
                != expected_hash.lower()
            ):
                # cleanup partially deployed files
                try:
                    if target_dir.exists():
                        shutil.rmtree(target_dir)
                except OSError:
                    pass
                raise RuntimeError(
                    f"Payload checksum mismatch after deployment: {relative_name}"
                )

        # 2. Update environmental parameters
        if add_to_path:
            self.append_to_user_path(str(target_dir))

        # 3. Create Desktop link architecture
        if create_shortcut:
            self.create_windows_shortcut(
                gui_exe_path if gui_exe_path.exists() else exe_path
            )

        # 4. Create uninstaller and register with Windows
        uninstaller_path = self.create_uninstaller(target_dir)
        try:
            self.register_uninstall_entry(uninstaller_path)
        except OSError:
            # non-fatal: leave installation but warn via return
            pass

        return target_dir

    def create_uninstaller(self, target_dir: Path):
        """Create a simple uninstaller batch script that removes files and registry entries."""
        uninstall_bat = target_dir / "uninstall.bat"
        desktop_shortcut = (
            Path(os.environ.get("USERPROFILE", "")) / "Desktop" / f"{self.app_name}.lnk"
        )
        # PowerShell snippet to remove PATH entry and uninstall registry key then delete folder
        escaped_target = str(target_dir).replace("'", "''")
        escaped_shortcut = str(desktop_shortcut).replace("'", "''")
        ps = (
            "$ErrorActionPreference = 'SilentlyContinue';\n"
            f"$appPath = '{escaped_target}';\n"
            f"$shortcut = '{escaped_shortcut}';\n"
            "# Remove PATH entry from current user environment\n"
            "$envKey = 'HKCU:\\Environment'\n"
            "$p = (Get-ItemProperty -Path $envKey -Name Path -ErrorAction SilentlyContinue).Path\n"
            "if ($p) { $new = ($p -split ';' | Where-Object { $_ -ne '' -and $_ -ne $appPath }) -join ';'; Set-ItemProperty -Path $envKey -Name Path -Value $new }\n"
            "# Remove Uninstall registry key\n"
            f"$uKey = 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{self.app_name}'\n"
            "Remove-Item -Path $uKey -Recurse -Force -ErrorAction SilentlyContinue\n"
            "# Remove desktop shortcut and installed folder\n"
            "if (Test-Path $shortcut) { Remove-Item -Path $shortcut -Force -ErrorAction SilentlyContinue }\n"
            "Start-Sleep -Milliseconds 300\n"
            "Remove-Item -Path $appPath -Recurse -Force -ErrorAction SilentlyContinue\n"
        )

        with open(uninstall_bat, "w", encoding="utf-8") as f:
            f.write("@echo off\n")
            f.write(f'powershell -NoProfile -ExecutionPolicy Bypass -Command "{ps}"\n')
            f.write("exit /b 0\n")

        # make sure it's writable
        try:
            os.chmod(uninstall_bat, 0o755)
        except OSError:
            pass
        return uninstall_bat

    def register_uninstall_entry(self, uninstall_path: Path):
        """Register the uninstaller under the current user's Uninstall registry hive."""
        key_root = r"Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall"
        subkey = f"{self.app_name}"
        reg_path = key_root + "\\" + subkey
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, reg_path)
        try:
            winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, self.app_name)
            winreg.SetValueEx(key, "Publisher", 0, winreg.REG_SZ, self.vendor_name)
            winreg.SetValueEx(
                key, "UninstallString", 0, winreg.REG_SZ, str(uninstall_path)
            )
            winreg.SetValueEx(
                key, "QuietUninstallString", 0, winreg.REG_SZ, str(uninstall_path)
            )
        finally:
            winreg.CloseKey(key)

    def append_to_user_path(self, path_string):
        """Appends directory to the User Environment block and signals system refresh."""
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_ALL_ACCESS
        )
        try:
            try:
                current_path, _ = winreg.QueryValueEx(key, "Path")
            except FileNotFoundError:
                current_path = ""

            if path_string not in current_path.split(";"):
                new_path = (
                    f"{current_path};{path_string}" if current_path else path_string
                )
                winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, new_path)

                # Broadcaster call to update all running shells
                ctypes.windll.user32.SendMessageTimeoutW(
                    0xFFFF,
                    0x001A,
                    0,
                    "Environment",
                    0x0002,
                    5000,
                    ctypes.byref(ctypes.c_long()),
                )
        finally:
            winreg.CloseKey(key)

    def create_windows_shortcut(self, exe_path):
        """Creates an authenticated application launcher passing explicit CLI arguments."""
        try:
            import win32com.client

            shell = win32com.client.Dispatch("WScript.Shell")
            desktop = Path(os.environ["USERPROFILE"]) / "Desktop"
            shortcut_path = desktop / f"{self.app_name}.lnk"

            shortcut = shell.CreateShortCut(str(shortcut_path))
            shortcut.Targetpath = str(exe_path)
            shortcut.Arguments = "" if exe_path.name == "keyplus-gui.exe" else "--gui"
            shortcut.WorkingDirectory = str(exe_path.parent)
            shortcut.save()
        except ImportError:
            pass
