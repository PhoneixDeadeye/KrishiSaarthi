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
    """Derive a Fernet-compatible key from Django's SECRET_KEY."""
    secret = settings.SECRET_KEY.encode()
    # SHA-256 produces 32 bytes, base64-encode for Fernet's 44-char requirement
    digest = hashlib.sha256(secret).digest()
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
