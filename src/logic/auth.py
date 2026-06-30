# src/logic/auth.py

import hashlib
import os
from pathlib import Path

# Get user home directory
HOME = Path.home()

AUTH_DIR = HOME / ".local" / "share" / "ZFordDev" / "keyplus"
AUTH_FILE = Path("auth.db")

def create_password(password: str):
    """Hashes and saves the master password."""
    salt = os.urandom(16)
    hashed = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
    
    with open(AUTH_FILE, "wb") as f:
        f.write(salt + hashed)

def verify_password(password: str) -> bool:
    """Verifies the master password against the saved hash."""
    if not AUTH_FILE.exists():
        return False
        
    with open(AUTH_FILE, "rb") as f:
        data = f.read()
        
    salt = data[:16]
    saved_hash = data[16:]
    
    hashed = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
    return hashed == saved_hash

def password_exists() -> bool:
    return AUTH_FILE.exists()