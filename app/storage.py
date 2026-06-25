"""
app/storage.py
--------------

communication to the rust backend
"""

from keyplus_core import store_vault, load_vault
import json
import os

VAULT_PATH = "data/vault.json"

def load_vault_data():
    if not os.path.exists(VAULT_PATH):
        return {"entries": []}
    blob = load_vault(VAULT_PATH)
    return json.loads(blob)

def save_vault(data):
    os.makedirs("data", exist_ok=True)
    blob = json.dumps(data, indent=2)
    store_vault(VAULT_PATH, blob)
