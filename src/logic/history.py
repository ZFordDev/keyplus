# src/logic/history.py

from .storage.storage import load_vault_raw, save_vault_raw
from .session import ensure_session_key
from datetime import datetime


def _now():
    return datetime.utcnow().isoformat()


# ---------------------------------------------------------
# Get history for an entry
# ---------------------------------------------------------

def get_history(identifier: str):
    ensure_session_key()
    vault = load_vault_raw()

    for entry in vault.get("entries", []):
        if entry["id"] == identifier or entry["name"] == identifier:
            return entry.get("history", [])

    return []


# ---------------------------------------------------------
# Append a history record
# ---------------------------------------------------------

def add_history(identifier: str, old_password: str):
    ensure_session_key()
    vault = load_vault_raw()

    for entry in vault.get("entries", []):
        if entry["id"] == identifier or entry["name"] == identifier:

            if "history" not in entry:
                entry["history"] = []

            entry["history"].append({
                "password": old_password,
                "timestamp": _now()
            })

            save_vault_raw(vault)
            return

    # If entry not found, do nothing
    return
