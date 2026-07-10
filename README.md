<!-- ========================================================= -->
<!-- Standards Approval Badge (not up to standards yet) -->
<!-- ========================================================= -->
<!--
<table align="right">
  <tr>
    <td>
      <img src="https://raw.githubusercontent.com/ZFordDev/ZFordDev/main/assets/standards-approved.svg" width="80" alt="ZFordDev Standards Approved Badge">
    </td>
  </tr>
</table> 
-->

<!-- ========================================================= -->
<!-- Required Badges -->
<!-- ========================================================= -->

[![Docs](https://img.shields.io/badge/DocsHub-docs.zford.dev-4F46E5?style=flat-square)](https://docs.zford.dev/zforddev/keyplus/)
![Status](https://img.shields.io/badge/Status-ACTIVE-4CAF50?style=flat-square)
![Linux](https://img.shields.io/badge/Linux-FCC624?style=flat-square&logo=linux&logoColor=black)
![Windows](https://img.shields.io/badge/Windows-0078D4?style=flat-square&logo=windows&logoColor=white)
![Python](https://img.shields.io/badge/Built_with-Python-blue?style=flat-square)

# KeyPlus  
*A completely offline, local‑first password manager.*

> **Version:** v0.2.8 
> **Status:** Beta • Actively Developed • Accepting Contributions

---

## Why KeyPlus Exists

My password storage leaked.  
My offline manager went paid.  
I needed something I could trust.

So I built KeyPlus — a local‑only password vault that stays on your machine, stays simple, and stays yours.

---

## Overview

KeyPlus is a clean, local‑first password vault built around one idea:

**Add passwords quickly. View passwords quickly. Trust the tool because it never leaves your machine.**

The design is intentionally straightforward:

- Use the CLI when you want speed  
- Use the GUI (coming soon) when you want comfort  
- Keep the vault secure, structured, and namespace-isolated  
- Keep everything offline, always  

KeyPlus isn’t trying to be an ecosystem or a platform.  
It’s a tool: fast to open, fast to use, and built to stay yours.

---

## Features

### **Current (v0.1.2)**
- **Authenticated Access Engine:** Master password verification powered by memory-hard `Argon2` hashing.
- **Whole-Vault Encryption:** Strong authenticated symmetric encryption via `cryptography` (Fernet AES-128 in CBC mode with HMAC).
- **SQLite Storage Backend:** Drop-in structured database management utilizing isolated user namespace matching `~/.local/share/ZFordDev/keyplus/`.
- **Interactive CLI REPL:** Snappy terminal runtime loop allowing fast entry addition, reading, and editing.
- **Security-First Session Timeout:** Smart session tracking that automatically locks down the interactive console if left idle.
- **Password History Tracking:** Deep change detection to maintain fallback historical states when rotating credentials.

### **In Development**
- Search and filtering via CLI
- Bulk import/export modules (.csv, unencrypted JSON)
- Lightweight desktop UI interface launcher (`Flet` canvas)
- Strict Snapcraft build configurations for verified Linux packaging

---

## Requirements

KeyPlus runs on any system with:

### **Python**
- Python 3.10+  
- Pip + venv recommended  

### **Supported Platforms**
- Linux  
- Windows  
- macOS (planned)

---

## Quick Start (From Source)

```bash
git clone [https://github.com/ZFordDev/keyplus.git](https://github.com/ZFordDev/keyplus.git)
cd keyplus

# Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install KeyPlus in editable development mode
pip install -e .

```

Run the CLI:

```bash
keyplus

```

---

## Project Structure

```text
keyplus/
├── src/
│   └── keyplus/            # Core package namespace root
│       ├── cli/            # CLI Command Interface & REPL loop
│       ├── ui/             # Pyside6 Ui
│       └── logic/          # Core cryptography & database operations
│           └── storage/    # SQLite connections
├── LICENSE
├── README.md
├── pyproject.toml          # Modern PEP 621 packaging definitions
└── temp_notes.md           # Internal scratchpad

```

*Note: Runtime data is safely kept out of the codebase repository and isolates directly to `~/.local/share/ZFordDev/keyplus/` on Linux architectures.*

---

## Roadmap

* Packaging
  * linux
    * deb ✔️
    * snap ⏳
  * Windows
  * mac 🛠️
  * android? 🤔

---

## Contributing

Contributions, bug reports, and feature requests are welcome.

See:

* [STANDARDS.md](https://github.com/ZFordDev/ZFordDev/blob/main/STANDARDS.md) for ecosystem‑wide expectations

---

## Security

KeyPlus uses verified, top-tier cryptographic primitives (`Argon2id` and `Fernet` AES-authenticated encryption). Data is kept strictly sandbox-local.

A formal security audit blueprint will accompany full beta milestone tags.

---

## License

Released under the MIT License.

See `LICENSE` for details.

---

## About ZFordDev

KeyPlus is part of the ZFordDev ecosystem — a collection of practical, long‑term tools built with clarity, simplicity, and maintainability in mind.
