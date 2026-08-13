# KeyPlus Security Policy

KeyPlus handles sensitive local data, but it has not received an independent security audit. No claim of complete protection, secure erasure, or suitability for every threat model is made.

## Reporting a vulnerability

Use a private GitHub security advisory in the KeyPlus repository. Do not open a public issue containing exploit details and do not attach real vaults, passwords, or credentials.

Include, where possible:

- affected KeyPlus version and package type;
- operating system;
- concise reproduction steps using synthetic data;
- expected and observed behavior;
- likely impact.

## Supported versions

During 0.3 development, fixes target the current development line. KeyPlus 0.2 uses the legacy working-directory format and should be migrated once 0.3 is released and verified for the user's environment.

## Security boundaries

The encrypted vault does not protect against an already-compromised operating-system account, malware running as the user, keyloggers, screen capture, weak master passwords, or secrets displayed or copied by the user. Python does not provide guaranteed secure memory erasure.
