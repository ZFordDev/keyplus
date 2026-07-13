[![Docs](https://img.shields.io/badge/DocsHub-docs.zford.dev-4F46E5?style=flat-square)](https://docs.zford.dev/zforddev/keyplus/)
![Status](https://img.shields.io/badge/Status-ACTIVE-4CAF50?style=flat-square)
![Linux](https://img.shields.io/badge/Linux-FCC624?style=flat-square&logo=linux&logoColor=black)
![Windows](https://img.shields.io/badge/Windows-0078D4?style=flat-square&logo=windows&logoColor=white)  
![Downloads](https://img.shields.io/github/downloads/ZFordDev/keyplus/total?style=flat-square)
![Python](https://img.shields.io/badge/Built_with-Python-blue?style=flat-square)


# KeyPlus  
*A completely offline, local‑first password manager.*

> **Version:** v0.2.9  
> **Status:** Beta • Actively Developed • Accepting Contributions

## Why KeyPlus Exists

My password storage leaked.  
My offline manager went paid.  
I needed something I could trust.

So I built KeyPlus, a local‑only password vault that stays on your machine, stays simple, and stays yours.

## Features

### **Current**
- **Argon2 master password verification**  
  - Memory‑hard hashing so brute‑forcing is a bad time.
- **Full vault encryption**  
  - AES‑backed symmetric encryption with authenticated access.
- **SQLite storage**  
  - Structured, isolated, and stored under ~/.local/share/ZFordDev/keyplus/.
- **Interactive CLI**  
  - Quick add, quick read, quick edit.
- **Session timeout**  
  - Leave the CLI idle and it locks itself.
- **Password history**  
  - Keeps old versions when you rotate credentials.

### **In Development**
- CLI search + filtering
- Import/export (CSV, JSON)
- Snapcraft packaging for Linux
- Windows installer (custom)
- macOS support (maby)

> [!TIP]
> **Where is the updater?!**  
> If you know my work, you know I always ship an updater so you don’t have to keep checking GitHub for new versions.  
> 
> KeyPlus will get one I’m just being careful with it.  
> 
> The logic is easy.  
> The safe part is hard.  
>
>Password managers are sensitive tools, and I’m not going to rush an auto‑update system that touches encrypted vaults. When I’m confident the updater can be done securely (and without breaking your vault), it’ll land.

## Quick Start (From Source)

```bash
git clone https://github.com/ZFordDev/keyplus.git
cd keyplus

python3 -m venv .venv
source .venv/bin/activate

pip install -e .
keyplus
```

## Project Structure

```text
keyplus/
├── src/keyplus/
│   ├── cli/        # CLI + REPL
│   ├── ui/         # GUI layer (PySide6)
│   └── logic/      # crypto + database
│       └── storage/
├── pyproject.toml
├── README.md
└── LICENSE
```

*Note: Runtime data stays outside the repo and lives in your user namespace.*

## Packaging roadmap

* Packaging
  * linux
    * deb ✔️
    * snap ⏳
  * Windows ⏳
    * .exe ⏳
      * Custom installer⏳
  * mac 🛠️
  * android? 🤔

## Expectations

KeyPlus is actively developed, but it’s still growing.
It works, it’s stable, and it’s offline but new features land regularly.

If you want something simple and local‑first, you’ll probably like it.
If you want cloud sync, autofill, or browser extensions… this isn’t that.

## Contributing
Issues, ideas, PRs — all welcome.

## License

Released under the MIT License.

See `LICENSE` for details.

## About ZFordDev

KeyPlus is part of the ZFordDev ecosystem — a collection of practical, long‑term tools built with clarity, simplicity, and maintainability in mind.


<table align="right">
  <tr>
    <td>
      <img src="https://raw.githubusercontent.com/ZFordDev/ZFordDev/main/assets/standards-approved.svg" width="80" alt="ZFordDev Standards Approved Badge">
    </td>
  </tr>
</table>