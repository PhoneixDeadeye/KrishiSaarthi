"""
Field-level encryption utilities using Fernet symmetric encryption.
Used to encrypt sensitive data at rest (bank accounts, IFSC codes).
"""
import base64
import hashlib
from django.conf import settings
from django.db import models
from cryptography.fernet import Fernet, InvalidToken


def _get_fernet_key() -> bytes:
    """Get a Fernet-compatible key from settings.FERNET_KEYS.

    Accepts either:
    - A valid 44-char urlsafe base64 Fernet key.
    - An arbitrary string, which is deterministically hashed into a Fernet key.
    """
    configured = getattr(settings, "FERNET_KEYS", []) or []
    candidate = str(configured[0]).encode() if configured else settings.SECRET_KEY.encode()
    try:
        # Already a valid Fernet key
        Fernet(candidate)
        return candidate
    except Exception:
        # Convert arbitrary secret to Fernet-compatible key
        digest = hashlib.sha256(candidate).digest()
        return base64.urlsafe_b64encode(digest)


def _get_fernet() -> Fernet:
    return Fernet(_get_fernet_key())


def encrypt_value(plaintext: str) -> str:
    """Encrypt a string value. Returns base64-encoded ciphertext."""
    if not plaintext:
        return plaintext
    f = _get_fernet()
    return f.encrypt(plaintext.encode()).decode()


def decrypt_value(ciphertext: str) -> str:
    """Decrypt a base64-encoded ciphertext. Returns plaintext string."""
    if not ciphertext:
        return ciphertext
    f = _get_fernet()
    try:
        return f.decrypt(ciphertext.encode()).decode()
    except (InvalidToken, Exception):
        # If decryption fails (e.g., data was stored before encryption),
        # return the raw value as-is for backward compatibility
        return ciphertext


class EncryptedCharField(models.CharField):
    """
    A CharField that transparently encrypts data at rest.
    Values are encrypted before saving to DB and decrypted on retrieval.
    """

    def get_prep_value(self, value):
        """Encrypt before saving to database."""
        value = super().get_prep_value(value)
        if value:
            return encrypt_value(value)
        return value

    def from_db_value(self, value, expression, connection):
        """Decrypt when reading from database."""
        if value:
            return decrypt_value(value)
        return value

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        # Use this module path so migrations reference the right class
        path = "config.encryption.EncryptedCharField"
        return name, path, args, kwargs
