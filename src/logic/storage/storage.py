# src/logic/storage/storage.py

import sqlite3
from pathlib import Path

# Get user home directory
HOME = Path.home()

# ---------------------------------------------------------
# Vault Database location under unified ZFordDev namespace
# ---------------------------------------------------------

VAULT_DIR = HOME / ".local" / "share" / "ZFordDev" / "keyplus"
DB_FILE = VAULT_DIR / "vault.db"

# Ensure the directory exists safely
VAULT_DIR.mkdir(parents=True, exist_ok=True)


def _get_connection():
    """Establish a connection to the SQLite database and initialize tables."""
    conn = sqlite3.connect(str(DB_FILE))
    
    # Enable Write-Ahead Logging (WAL)
    conn.execute("PRAGMA journal_mode=WAL;")
    
    # Create the single-row vault table if it doesn't exist
    conn.execute("""
        CREATE TABLE IF NOT EXISTS vault_store (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            ciphertext TEXT NOT NULL
        );
    """)
    conn.commit()
    return conn


# ---------------------------------------------------------
# Load vault
# ---------------------------------------------------------

def load_vault_raw() -> dict:
    """Retrieve the vault data row. If missing, return an empty payload structure."""
    conn = _get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT ciphertext FROM vault_store WHERE id = 1;")
        row = cursor.fetchone()
        
        if not row:
            # Table is empty, treat it like a missing JSON file
            return {"entries": []}
            
        return {"ciphertext": row[0]}
    finally:
        conn.close()


# ---------------------------------------------------------
# Save vault
# ---------------------------------------------------------

def save_vault_raw(vault: dict):
    """Upsert the encrypted ciphertext string into the database single-row store."""
    ciphertext = vault.get("ciphertext", "")
    
    conn = _get_connection()
    try:
        # Using SQLite's UPSERT syntax to keep the row locked to id=1
        conn.execute("""
            INSERT INTO vault_store (id, ciphertext) 
            VALUES (1, ?)
            ON CONFLICT(id) DO UPDATE SET ciphertext = excluded.ciphertext;
        """, (ciphertext,))
        conn.commit()
    finally:
        conn.close()