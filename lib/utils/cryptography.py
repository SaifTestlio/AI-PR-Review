"""
This module provides encryption and decryption functionality for secure data handling.

The SecretManager class handles:
- Encrypting strings using Fernet symmetric encryption
- Decrypting previously encrypted strings
- Base64 encoding/decoding of encrypted data

Key features:
- Secure encryption using the cryptography.fernet module
- String-based input/output with automatic encoding handling
- Base64 encoding for safe storage and transmission
- Simple API for encryption and decryption operations
"""
import base64
import pytest
from cryptography.fernet import Fernet, InvalidToken

class SecretManager:
    """Class to encrypt and decrypt strings"""

    @staticmethod
    def generate_key() -> str:
        """Generate a new Fernet key and return it as a string"""
        return Fernet.generate_key().decode()

    def __init__(self, key: str):
        self.fernet = Fernet(key)

    def encrypt(self, data: str) -> str:
        """Encrypt a string and return base64 encoded string"""
        return base64.b64encode(
            self.fernet.encrypt(data.encode())
        ).decode()

    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt a base64 encoded encrypted string"""
        return self.fernet.decrypt(
            base64.b64decode(encrypted_data.encode())

        ).decode()

class TestSecretManager:
    """Test suite for SecretManager class"""

    @pytest.fixture
    def secret_manager(self):
        """Create a SecretManager instance with a new key for testing"""
        key = SecretManager.generate_key()
        return SecretManager(key)

    def test_key_generation(self):
        """Test that generated keys are valid and unique"""
        key1 = SecretManager.generate_key()
        key2 = SecretManager.generate_key()

        assert isinstance(key1, str)
        assert len(key1) > 0
        assert key1 != key2

    def test_encryption_decryption(self, secret_manager):
        """Test basic encryption and decryption functionality"""
        original_text = "Hello, World!"
        encrypted = secret_manager.encrypt(original_text)
        decrypted = secret_manager.decrypt(encrypted)

        assert encrypted != original_text
        assert decrypted == original_text

    def test_empty_string(self, secret_manager):
        """Test handling of empty strings"""
        empty = ""
        encrypted = secret_manager.encrypt(empty)
        decrypted = secret_manager.decrypt(encrypted)

        assert encrypted != empty
        assert decrypted == empty

    def test_different_keys(self):
        """Test that different keys produce different encryption results"""
        text = "Test message"
        sm1 = SecretManager(SecretManager.generate_key())
        sm2 = SecretManager(SecretManager.generate_key())

        enc1 = sm1.encrypt(text)
        enc2 = sm2.encrypt(text)

        assert enc1 != enc2

        with pytest.raises(InvalidToken):
            sm2.decrypt(enc1)

    def test_invalid_encrypted_data(self, secret_manager):
        """Test handling of invalid encrypted data"""
        with pytest.raises(Exception):
            secret_manager.decrypt("invalid-data")

    def test_special_characters(self, secret_manager):
        """Test encryption/decryption of special characters"""
        special_text = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        encrypted = secret_manager.encrypt(special_text)
        decrypted = secret_manager.decrypt(encrypted)

        assert decrypted == special_text
