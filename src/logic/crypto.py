# src/logic/crypto.py

import base64
import hashlib
from cryptography.fernet import Fernet

def _derive_fernet_key(session_key: str) -> bytes:
    """
    Fernet requires a 32-byte url-safe base64 encoded key.
    We hash the session key using SHA-256 to ensure it's exactly 32 bytes.
    Thank you UniSQ!
    """
    key_bytes = session_key.encode("utf-8")
    hashed = hashlib.sha256(key_bytes).digest()
    return base64.urlsafe_b64encode(hashed)


def encrypt(data: str, key: str) -> str:
    """Encrypt a plaintext string using the session key."""
    if not data:
        return ""
    
    fernet_key = _derive_fernet_key(key)
    f = Fernet(fernet_key)
    
    encrypted_bytes = f.encrypt(data.encode("utf-8"))
    return encrypted_bytes.decode("utf-8")


def decrypt(data: str, key: str) -> str:
    """Decrypt a ciphertext string using the session key."""
    if not data:
        return ""
    
    try:
        fernet_key = _derive_fernet_key(key)
        f = Fernet(fernet_key)
        
        decrypted_bytes = f.decrypt(data.encode("utf-8"))
        return decrypted_bytes.decode("utf-8")
    except Exception:
        # Raises if the file is corrupted or an incorrect session key/master password was used
        raise ValueError("Decryption failed. Invalid key or corrupted data.")