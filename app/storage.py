"""
app/storage.py
--------------

communication to the rust backend
"""

from keyplus_core import temp_store_vault, temp_load_vault
import json
import os

VAULT_PATH = "data/vault.json"

def load_vault_data():
    blob = temp_load_vault(VAULT_PATH)
    return json.loads(blob)

def save_vault(data):
    os.makedirs("data", exist_ok=True)
    blob = json.dumps(data, indent=2)
    temp_store_vault(VAULT_PATH, blob)
