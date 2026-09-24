<div align="center">

# KeyPlus

### local-first encrypted password vault with terminal and desktop interface.

[Documentation](https://docs.zford.dev/zforddev/keyplus/) · [Downloads](https://github.com/ZFordDev/keyplus/releases) · [Report a bug](https://github.com/ZFordDev/keyplus/issues/new/choose)


[![Status](https://img.shields.io/badge/status-active-4CAF50?style=flat-square)](https://github.com/ZFordDev/keyplus)
[![Platforms](https://img.shields.io/badge/platforms-Windows%20%7C%20Linux-0078D4?style=flat-square)](#installation)
[![GitHub downloads](https://img.shields.io/github/downloads/ZFordDev/keyplus/total?style=flat-square)](https://github.com/ZFordDev/keyplus/releases)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue?style=flat-square)](LICENSE)


</div>

> [!WARNING]
> **Project Status: Archived / Deprecated**
> This project is no longer maintained or used. It has not undergone security audits and should NOT be used for managing real credentials.

> **Development status:** KeyPlus 0.3 is an architecture and data-safety release under active development. It has not received an independent security audit. Keep an independent backup of important credentials and evaluate the software for your own risk requirements.

## What changed in 0.3

- CLI and GUI now use one shared `VaultService`.
- The default vault has one deterministic per-user location rather than following the shell working directory.
- Authentication results from successfully decrypting one self-contained, versioned vault file.
- Argon2id derives a 256-bit key and AES-GCM provides authenticated encryption.
- Vault writes use a same-directory temporary file and atomic replacement.
- POSIX data directories and vault files are explicitly restricted to `0700` and `0600` respectively.
- Mutations use an advisory lock and reject stale concurrent writers.
- Explicit locking invalidates the shared session as far as practical in Python.
- KeyPlus 0.2 `auth.db` plus `vault.json` pairs can be migrated without modifying the originals.

These mechanisms do not protect a vault from malware, keyloggers, screen capture, a compromised user account, weak master passwords, or every implementation defect.

## Interfaces

Start the interactive CLI:

```bash
keyplus
```

Start the desktop interface:

```bash
keyplus --gui
```

Desktop-oriented packages may also install the equivalent `keyplus-gui` launcher.

The CLI supports `list`, `view`, `add`, `edit`, `delete`, `backup`, `backups`, `restore <path>`, `passwd`, `lock`, and `help`. Credential and master passwords are collected with hidden input rather than inline command arguments.

The GUI supports vault setup and unlock, listing, adding, viewing, editing, and deleting entries, changing the master password, creating encrypted backups, and restoring a validated backup from the login screen. Logout calls the same core lock operation as the CLI.

## Data locations

The default vault filename is `keyplus.vault`.

- Linux: `$XDG_DATA_HOME/ZFordDev/KeyPlus/`, falling back to `~/.local/share/ZFordDev/KeyPlus/`
- Snap: `$SNAP_USER_COMMON/KeyPlus/`
- Windows: `%LOCALAPPDATA%\ZFordDev\KeyPlus\`

Encrypted backups are stored in the `backups` directory beneath the same data directory. Application packages use the same path resolver and vault format.

## Migrating a 0.2 vault

KeyPlus 0.2 stored `auth.db` and `vault.json` in the directory from which it was launched.

The CLI checks its current directory for that pair on first 0.3 launch. An explicit directory can be supplied with:

```bash
keyplus --migrate /path/to/legacy/folder
```

The GUI setup screen provides **Migrate a KeyPlus 0.2 Vault**. Successful migration creates and validates the 0.3 vault but leaves both original files unchanged.

Do not delete the legacy files until you have independently confirmed the migrated vault and your backup strategy.

## Install from source

KeyPlus requires Python 3.10 or later.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
python -m pytest
keyplus
```

Windows activation uses `.venv\Scripts\activate`.

## Snap packaging

The committed `snap/snapcraft.yaml` is the authoritative Snapcraft project.
Canonical's Snap Store build service is linked to the repository and builds
from `main`; GitHub Actions validates the same manifest but does not publish to
the Store or hold Store credentials.

## Project structure

```text
src/keyplus/
├── application/   # models, validation, errors, and VaultService
├── security/      # Argon2id, AES-GCM, and unlocked session state
├── storage/       # paths, format, atomic repository, locking, migration
├── cli/           # terminal presentation and REPL routing
├── ui/gui/        # PySide6 presentation
├── bootstrap.py   # shared composition root
└── __main__.py    # installed entry point
```

## Deliberate non-features

KeyPlus 0.3 does not currently provide cloud synchronization, browser integration, autofill, password generation, plaintext import/export, password history, or an application-managed updater.

## Development checks

```bash
python -m pytest -q
python -m ruff check src tests
python -m ruff format --check src tests
```

## Security reporting

Please use a private GitHub security advisory for suspected vulnerabilities. Do not include real vault files, master passwords, or credentials in reports. See `SECURITY.md`.

KeyPlus is licensed under the MIT License.
