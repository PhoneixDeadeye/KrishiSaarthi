"""
Tests for the encryption module (config.encryption).
"""
import pytest
from unittest.mock import patch
from config.encryption import encrypt_value, decrypt_value, EncryptedCharField


class TestEncryptDecrypt:
    """Tests for encrypt_value / decrypt_value functions."""

    def test_round_trip(self):
        """Encrypt then decrypt returns original value."""
        original = "1234567890123456"
        encrypted = encrypt_value(original)
        assert encrypted != original
        assert decrypt_value(encrypted) == original

    def test_empty_string_passthrough(self):
        """Empty strings are returned as-is."""
        assert encrypt_value("") == ""
        assert decrypt_value("") == ""

    def test_none_passthrough(self):
        """None values are returned as-is."""
        assert encrypt_value(None) is None
        assert decrypt_value(None) is None

    def test_encrypted_value_is_different(self):
        """Encrypted output should differ from plaintext."""
        plaintext = "SBIN0001234"
        encrypted = encrypt_value(plaintext)
        assert encrypted != plaintext
        assert len(encrypted) > len(plaintext)

    def test_decrypt_invalid_token_returns_raw(self):
        """Backward compat: if ciphertext is invalid, return raw value."""
        raw = "not-encrypted-data"
        result = decrypt_value(raw)
        assert result == raw

    def test_different_plaintexts_produce_different_ciphertexts(self):
        """Different inputs produce different outputs."""
        a = encrypt_value("account_a")
        b = encrypt_value("account_b")
        assert a != b


class TestEncryptedCharField:
    """Tests for the EncryptedCharField model field."""

    def test_get_prep_value_encrypts(self):
        field = EncryptedCharField(max_length=200)
        prep = field.get_prep_value("test1234")
        assert prep != "test1234"
        assert decrypt_value(prep) == "test1234"

    def test_get_prep_value_empty(self):
        field = EncryptedCharField(max_length=200)
        assert field.get_prep_value("") == ""

    def test_deconstruct_path(self):
        field = EncryptedCharField(max_length=200)
        name, path, args, kwargs = field.deconstruct()
        assert path == "config.encryption.EncryptedCharField"
