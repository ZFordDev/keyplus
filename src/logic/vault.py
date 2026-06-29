# src/logic/vault.py

import json
import uuid
from datetime import datetime
from .storage.storage import load_vault_raw, save_vault_raw
from .crypto import encrypt, decrypt
from .session import ensure_session_key
from .history import add_history

def _now():
    # Keep it clean with standard UTC
    return datetime.utcnow().isoformat()


# ---------------------------------------------------------
# Load vault
# ---------------------------------------------------------

def load_vault() -> dict:
    key = ensure_session_key()
    raw = load_vault_raw()
    
    # If it's a freshly initialized empty vault structure, skip decryption
    if not raw.get("entries") and "ciphertext" not in raw:
        return {"entries": []}
        
    ciphertext = raw.get("ciphertext")
    if not ciphertext:
        return {"entries": []}

    # Decrypt the payload back into its original JSON string
    plaintext_json = decrypt(ciphertext, key)
    return json.loads(plaintext_json)


# ---------------------------------------------------------
# Save vault
# ---------------------------------------------------------

def save_vault(vault: dict):
    key = ensure_session_key()
    
    # Turn the raw runtime dictionary into a flat string
    plaintext_json = json.dumps(vault)
    
    # Encrypt the entire string block
    ciphertext = encrypt(plaintext_json, key)
    
    # Pack it securely into the storage engine
    encrypted_vault = {"ciphertext": ciphertext}
    save_vault_raw(encrypted_vault)

# ---------------------------------------------------------
# CRUD operations
# ---------------------------------------------------------

def list_entries():
    vault = load_vault()
    return vault["entries"]


def get_entry(identifier: str):
    vault = load_vault()
    for e in vault["entries"]:
        if e["id"] == identifier or e["name"] == identifier:
            return e
    return None


def add_entry(name: str, domain: str, password: str):
    vault = load_vault()

    entry = {
        "id": str(uuid.uuid4()),
        "name": name,
        "domain": domain,
        "password": password,
        "created": _now(),
        "updated": _now(),
    }

    vault["entries"].append(entry)
    save_vault(vault)
    return entry


def edit_entry(identifier: str, **updates):
    # Use proper crypto-aware wrapper instead of load_vault_raw
    vault = load_vault()

    for entry in vault.get("entries", []):
        if entry["id"] == identifier or entry["name"] == identifier:

            old_password = entry["password"]

            # Apply updates
            for k, v in updates.items():
                if v is not None:
                    entry[k] = v

            entry["updated"] = _now()

            # Record history ONLY if password changed
            if "password" in updates and updates["password"] != old_password:
                add_history(identifier, old_password)

            # Use your proper crypto-aware wrapper instead of save_vault_raw
            save_vault(vault)
            return entry

    return None