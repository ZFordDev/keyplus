# src/logic/vault.py

import json
from pathlib import Path
from .crypto import encrypt, decrypt
from .session import ensure_session_key

# Get user home directory
HOME = Path.home()

VAULT_DIR = HOME / ".local" / "share" / "ZFordDev" / "keyplus"
VAULT_FILE = Path("vault.json")

def load_vault() -> list:
    """Loads and decrypts the vault entries."""
    if not VAULT_FILE.exists():
        return []
        
    key = ensure_session_key()
    
    with open(VAULT_FILE, "r") as f:
        ciphertext = f.read()
        
    if not ciphertext:
        return []
        
    plaintext_json = decrypt(ciphertext, key)
    return json.loads(plaintext_json)

def save_vault(entries: list):
    """Encrypts and saves the vault entries."""
    key = ensure_session_key()
    plaintext_json = json.dumps(entries)
    ciphertext = encrypt(plaintext_json, key)
    
    with open(VAULT_FILE, "w") as f:
        f.write(ciphertext)

def list_entries() -> list:
    return load_vault()

def add_entry(name: str, domain: str, password: str) -> dict:
    entries = load_vault()
    
    import uuid
    import datetime
    
    entry = {
        "id": str(uuid.uuid4()),
        "name": name,
        "domain": domain,
        "password": password,
        "created": datetime.datetime.now().isoformat(),
        "updated": datetime.datetime.now().isoformat()
    }
    
    entries.append(entry)
    save_vault(entries)
    return entry

def get_entry(entry_id: str) -> dict:
    entries = load_vault()
    for e in entries:
        if e["id"] == entry_id:
            return e
    return None