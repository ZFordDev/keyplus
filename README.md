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
<!-- ========================================================= -->

<!-- Optional Badges (Uncomment if applicable) -->

<!-- ========================================================= -->
<!--[![itch.io](https://img.shields.io/badge/itch.io-KeyPlus-FA5C5C?style=flat-square)](https://zforddev.itch.io/keyplus)-->
<!--[Downloads](https://img.shields.io/github/downloads/ZFordDev/keyplus/total?style=flat-square)-->
![Python](https://img.shields.io/badge/App_Built_with-Python-blue?style=flat-square) 
![Rust](https://img.shields.io/badge/Core_Built_with-Rust-orange?style=flat-square)

# KeyPlus  
*A completely offline, local-first password manager.*

> **Status:**  
> Pre‑Alpha • Actively Developed • Accepting Contributions soon

---

## Why KeyPlus Exists

My password storage leaked.

My offline manager went paid.

I needed something I could trust.

So I built KeyPlus — a local‑only password vault that stays on your machine, stays simple, and stays yours.

---

## Overview

KeyPlus is a simple, local‑only password vault built around one idea:

Add passwords quickly. View passwords quickly. Trust the tool because it never leaves your machine.

The design is intentionally straightforward:

- Use the CLI when you want speed
- Use the GUI when you want comfort
- Keep the vault format predictable and transparent
- Keep everything offline, always

KeyPlus isn’t trying to be an ecosystem or a platform.
It’s a tool: fast to open, fast to use, and built to stay yours.

---

## Features (Current & Planned)

### Current
- Local‑first vault storage  
- Rust‑backed read/write operations  
- JSON‑based vault format  
- Simple CLI interface  
- Cross‑platform support (Linux, Windows, macOS soon)

### In Development
- Encrypted vault format 
- Entry creation, editing, and deletion  
- Search and filtering  
- Import/export tools  
- UI launcher (Python + TUI or lightweight GUI)  
- Vault versioning and migration system  

---

## Requirements

KeyPlus runs on any system with:

**Python**
- Python 3.10+  
- Pip + venv recommended  

**Rust**
- Rust toolchain (stable)  
- Required only for development builds  

**Supported Platforms**
- Linux  
- Windows  
- macOS (maybe)

---

## Quick Start (From Source)

```bash
git clone https://github.com/ZFordDev/keyplus.git
cd keyplus

# Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install KeyPlus (Rust backend will compile)
pip install .
```

Run the CLI:

```bash
keyplus
```

---

## Installation

### Linux / Windows (Source Install)
```bash
pip install keyplus
```

Binary releases will be available once the encryption layer stabilises.

---

## Project Structure

```
keyplus/
├── app/                    # Python UI + CLI
│   ├── keyplus.py          # Entry point
│   ├── storage.py          # Python ↔ Rust bridge
│   └── cli/                # CLI commands
│
├── core/                   # Rust backend
│   ├── src/lib.rs          # PyO3 module
│   └── Cargo.toml
│
├── README.md
├── pyproject.toml          # Maturin + Python packaging
└── temp_notes.md           # Internal notes
```

---

## Roadmap

KeyPlus will get a roadmap soon

---

## Known Issues

KeyPlus is in early development.  
Most features are still being built — check back as the vault, CLI, and encryption layer evolve.

---

## Contributing

Contributions, bug reports, and feature requests are welcome.

See:

<!-- - `CONTRIBUTING.md` for project‑specific guidelines -->
- [STANDARDS.md](https://github.com/ZFordDev/ZFordDev/blob/main/STANDARDS.md) for ecosystem‑wide expectations  

---

## Security

KeyPlus is local‑first and security‑focused.  
A full security policy will be published once the encryption layer is complete.

---

## License

Released under the MIT License.  
See `LICENSE` for details.

---

## About ZFordDev

KeyPlus is part of the ZFordDev ecosystem — a collection of practical, long‑term tools built with clarity, simplicity, and maintainability in mind.

---