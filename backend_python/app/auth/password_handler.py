import hashlib
import secrets
from typing import Tuple


def _generate_salt() -> str:
    """Generate a random salt for password hashing"""
    return secrets.token_hex(16)


def _hash_with_salt(password: str, salt: str) -> str:
    """Hash password with salt using SHA-256"""
    return hashlib.sha256((password + salt).encode()).hexdigest()


def hash_password(password: str) -> str:
    """Hash password using SHA-256 with salt"""
    salt = _generate_salt()
    hash_value = _hash_with_salt(password, salt)
    return f"{salt}:{hash_value}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against stored hash"""
    try:
        salt, stored_hash = hashed_password.split(":", 1)
        computed_hash = _hash_with_salt(plain_password, salt)
        return secrets.compare_digest(computed_hash, stored_hash)
    except ValueError:
        # Invalid hash format
        return False
