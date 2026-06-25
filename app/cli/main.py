"""
app/cli/main.py
---------------

Basic return pass
"""

from ..storage import load_vault_data

def main():
    print("KeyPlus (CLI mode)")
    vault = load_vault_data()
    print("Entries:", vault.get("entries", []))
