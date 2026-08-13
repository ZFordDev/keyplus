# KeyPlus

KeyPlus is a local-first encrypted password vault with an interactive terminal interface and a PySide6 desktop interface.

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

The CLI supports `list`, `view`, `add`, `edit`, `delete`, `backup`, `restore <path>`, `lock`, and `help`. Credential passwords are collected with hidden input rather than inline command arguments.

The GUI supports vault setup and unlock, listing, adding, viewing, editing, and deleting entries, creating encrypted backups, and restoring a validated backup from the login screen. Logout calls the same core lock operation as the CLI.

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
