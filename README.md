# **KeyPlus**

A completely offline, local‑first password manager.  
Because putting all your keys in someone else’s cloud is a bad idea — so I’m building my own.





---

## Overview

KeyPlus is a lightweight, security‑focused password manager designed around a simple idea:

> **Your passwords belong to you — not a cloud provider, not a sync service, not a server.**

KeyPlus stores all credentials **locally**, **encrypted**, and **only unlocked when you’re present**.  
No telemetry. No network calls. No hidden sync. No surprises.

---

## Core Pillars

- **100% Offline**  
  Everything stays on your machine. No cloud, no remote APIs, no metadata leaks.

- **Local‑First Security**  
  A single master password derives the encryption key.  
  Vault is unreadable at rest.

- **Minimalist by Design**  
  No bloat, no plugins, no “pro” features. Just secure credential storage.

- **SchedPlus‑Style Logic Core**  
  Clean modules, predictable flow, CLI + optional GUI — without the 10‑headed hydra.

- **Optional Biometric Unlock**  
  Windows Hello or Ubuntu’s Secret Service can unlock the vault without typing the master password.

---

## Architecture

```
keyplus/
│
├── main.py
├── core/
│   ├── crypto.py      # key derivation, AES‑GCM encryption/decryption
│   ├── vault.py       # load/save encrypted vault blob
│   ├── manager.py     # add/get/list/search credentials
│   └── session.py     # session timeout + unlock logic
│
├── platform/
│   ├── windows.py     # Windows Hello / DPAPI integration
│   └── linux.py       # libsecret / keyring integration
│
├── ui/
│   ├── cli.py         # command‑line interface
│   └── gui.py         # optional GUI (future)
│
└── data/
    └── vault.kp       # encrypted vault file
```





---

## Security Model

### **Master Password**  
The master password is the *true* cryptographic root.  
It is never stored, never cached, and never written to disk.

### **Key Derivation**  
KeyPlus uses PBKDF2 or scrypt to derive a 256‑bit AES key from the master password.

### **Encrypted Vault**  
All credentials are stored as a single encrypted blob using AES‑256‑GCM.  
At rest, the vault is unreadable noise.

### **Session Timeout**  
If more than 60 seconds pass since the last unlock, the in‑memory key is wiped.  
Next access requires re‑authentication.

### **Biometric Unlock (Optional)**  
If enabled, the derived AES key is encrypted using:
- **Windows Hello + DPAPI** on Windows  
- **libsecret / GNOME Keyring** on Ubuntu  

Biometric unlock decrypts the AES key without typing the master password.

---

## Features

- **Add credentials**  
- **List entries**  
- **Search by name**  
- **Masked password display**  
- **Reveal password on demand**  
- **Session auto‑lock**  
- **Biometric unlock**  
- **Portable encrypted vault file**  

---

## Usage (CLI)

```
# Initialize a new vault
keyplus init

# Add a credential
keyplus add github zach@example.com

# List entries
keyplus list

# Reveal a password
keyplus show github
```

---

## GUI (Optional / Future)

A minimal GUI will be available later, built on the same logic core.  
The UI is intentionally simple — think “KeePass Mini,” not “Electron monster.”

---

## File Format

The vault file (`vault.kp`) contains:

```
{
  "version": 1,
  "salt": "...",
  "nonce": "...",
  "ciphertext": "..."
}
```

Everything inside `ciphertext` is encrypted JSON.

---

## Threat Model

KeyPlus protects against:

- casual snooping  
- stolen laptop without login  
- reading the vault file directly  
- offline brute‑force attempts  
- reverse‑engineering the vault format  

KeyPlus does **not** protect against:

- active malware  
- compromised OS  
- memory scraping  
- hardware keyloggers  

This is a **practical** password manager — not a fantasy one.

---

## License

MIT — because security tools should be open, inspectable, and forkable.

---

## Philosophy

KeyPlus exists because:

- local‑first tools matter  
- cloud sync is a liability  
- simple security is better than complex insecurity  
- you should own your secrets  

If you want a password manager that respects your machine, your workflow, and your privacy — KeyPlus is it.

---
