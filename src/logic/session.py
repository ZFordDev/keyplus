# src/logic/session.py

import time
import secrets
from .auth import verify_password

_session_key = None
_session_expiry = 0
SESSION_TTL = 60  # seconds for now, make it a config later


def set_session_key(password: str):
    global _session_key, _session_expiry
    _session_key = secrets.token_hex(32)  # random session token
    _session_expiry = time.time() + SESSION_TTL



def get_session_key():
    global _session_key, _session_expiry
    if time.time() > _session_expiry:
        return None
    return _session_key


def ensure_session_key():
    key = get_session_key()
    if key:
        return key

    # re-auth

    while True:
        pw = input("Session expired — please enter password: ").strip()
        if verify_password(pw):
            set_session_key(pw)
            return _session_key
        print("Incorrect password.")
