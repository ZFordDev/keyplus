# src/logic/auth.py

import json
from pathlib import Path
from argon2 import PasswordHasher

# Get user home directory
HOME = Path.home()

# ---------------------------------------------------------
# Auth file location under unified ZFordDev namespace
# ---------------------------------------------------------

AUTH_DIR = HOME / ".local" / "share" / "ZFordDev" / "keyplus"
AUTH_FILE = AUTH_DIR / "auth.json"

# Ensure directory exists safely
AUTH_DIR.mkdir(parents=True, exist_ok=True)

# Initialize the Argon2 password hasher
ph = PasswordHasher()


# ---------------------------------------------------------
# Load auth file
# ---------------------------------------------------------

def load_auth() -> dict | None:
    """Load the auth file containing the master hash."""
    if not AUTH_FILE.exists():
        return None

    if AUTH_FILE.stat().st_size == 0:
        return None

    with open(AUTH_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return None


# ---------------------------------------------------------
# Save auth file
# ---------------------------------------------------------

def save_auth(data: dict):
    """Save the master hash configuration securely."""
    with open(AUTH_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


# ---------------------------------------------------------
# Check if password exists
# ---------------------------------------------------------

def password_exists() -> bool:
    """Check if a master password hash has already been initialized."""
    # Ensure it exists and isn't a corrupted 0-byte file
    return AUTH_FILE.exists() and AUTH_FILE.stat().st_size > 0


# ---------------------------------------------------------
# Create password
# ---------------------------------------------------------

def create_password(password: str):
    """Hash the master password and store it."""
    hashed = ph.hash(password)
    save_auth({"hash": hashed})


# ---------------------------------------------------------
# Verify password
# ---------------------------------------------------------

def verify_password(password: str) -> bool:
    """Verify the provided password against the stored master hash."""
    data = load_auth()
    if not data or "hash" not in data:
        return False

    try:
        ph.verify(data["hash"], password)
        return True
    except Exception:
        # Catches verification mismatches or corrupted hash formats gracefully
        return False