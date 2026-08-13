# Changelog

## 0.3.0 — in development

- Replaced separate `auth.db` and `vault.json` state with one versioned vault envelope.
- Replaced direct SHA-256/Fernet vault key handling with Argon2id and AES-GCM.
- Added deterministic Linux, Snap, and Windows data paths.
- Added atomic writes, advisory locking, stale-writer detection, private POSIX modes, and encrypted backups.
- Added validated encrypted-backup restoration while preserving the previous vault.
- Added encrypted-backup inventory and restore failure tests covering wrong
  passwords, unsupported versions, failed writes, filename collisions, and
  replacement of a damaged `last-good.vault`.
- Added a shared application service and lock/session model for CLI and GUI.
- Added CLI and GUI master-password change workflows with current-password
  reauthentication and preservation of the previous encrypted vault.
- Added safe, read-only migration from verified KeyPlus 0.2 file pairs.
- Rebuilt the interactive CLI around shared service commands and hidden password prompts.
- Removed disconnected SQLite/history code and misleading reset/export controls.
- Replaced the misleading setup deletion warning with accurate password-recovery guidance.
- Added core, migration, path, CLI, and GUI integration tests.
- Replaced GitHub-side Snap Store publishing with a committed Snapcraft project
  used by Canonical's repository-linked build service.

## 0.2.9

- Last release using the working-directory `auth.db` and `vault.json` format.
