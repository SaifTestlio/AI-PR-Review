"""
This module provides test data management functionality for test automation.

The module handles:
- Loading and processing test data from YAML files
- Automatic decryption of sensitive data
- Hierarchical data structure management
- Test-specific data retrieval

Key features:
- YAML-based test data storage
- Automatic secret decryption
- Hierarchical data access
- Secure handling of sensitive information
- Error handling for missing data

Usage:
    properties = FrameworkProperties(test_data_file="test_data.yml", encryption_key="key")
    manager = TestDataManager(properties)
    test_data = manager.get_test_data("login_test")
"""
import os
from pathlib import Path
from typing import Any, Dict
import unittest
from unittest.mock import Mock, patch, mock_open

import yaml

from lib.models import FrameworkProperties
from lib.utils.cryptography import SecretManager

class DataManager:
    """Class for managing test data"""
    def __init__(self, properties: FrameworkProperties):
        self.data_file = Path(os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            properties.test_data_file
        ))
        self.secret_manager = SecretManager(properties.encryption_key)
        self._data = self._load_data()

    def _load_data(self) -> Dict[str, Any]:
        """Load and process the test data file"""
        if not self.data_file.exists():
            raise FileNotFoundError(f"Test data file not found: {self.data_file}")

        with open(self.data_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        return self._process_secrets(data)

    def _process_secrets(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively process encrypted secrets in the data"""
        if isinstance(data, dict):
            return {
                key: self._process_secrets(value)
                for key, value in data.items()
            }

        if isinstance(data, list):
            return [self._process_secrets(item) for item in data]

        if isinstance(data, str) and data.startswith('ENC['):
            return self.secret_manager.decrypt(data[4:-1])

        return data

    def get_test_data(self, test_name: str) -> Dict[str, Any]:
        """Get test data for a specific test"""
        return self._data.get(test_name, {})

    def get_all_test_data(self) -> Dict[str, Any]:
        """Get the entire test data dictionary"""
        return self._data

class TestDataManager(unittest.TestCase):
    """Test cases for TestDataManager class"""

    class TestableDataManager(DataManager):
        """Subclass to expose protected methods for testing"""
        def load_data(self):
            """Expose protected method for testing"""
            return self._load_data()

        def process_secrets(self, data):
            """Expose protected method for testing"""
            return self._process_secrets(data)

        @property
        def data(self):
            """Expose protected _data property for testing"""
            return self._data

        @data.setter
        def data(self, value):
            """Setter for protected _data property for testing"""
            self._data = value

    def setUp(self):
        """Set up test fixtures"""
        properties = Mock(spec=FrameworkProperties)
        properties.test_data_file = "test_data.yml"
        properties.encryption_key = "m8e0EMDdBnV0I6SGz-H7v1CKgQhLSnNcEIS5K4-WD1o="
        self.manager = self.TestableDataManager(properties)
        enc_password = [
            "Z0FBQUFBQm5ZdHRXWkkyOEQ2Tjg5cXpCcEtuWmF0TncyRVY1M3pjQWlVbmpYTko0b0l2Q2htNHRsS3Z1Y2RoS",
            "lh2aE1EVHB2czl5ekxmVUZEcUdxNm1lRlJDQ2ExRGk2ZUE9PQ=="
        ]
        enc_api_key = [
            "Z0FBQUFBQm5ZdDByem42RVRKTW84Q1IwM1MwVUQ4S0tTN2lFdHI1c0RPZEw3Wk1CbTBZNXk0Tmk2REVmUDREY",
            "mxsbG5rM3J5S2RDRTZlQThpYjNWYmZvaEVrUnN0bUszRmc9PQ=="
        ]
        self.test_data = {
            "login_test": {
                "username": "test_user",
                "password": f"ENC[{''.join(enc_password)}]",
                "settings": {
                    "timeout": 30,
                    "api_key": f"ENC[{''.join(enc_api_key)}]"
                }
            },
            "search_test": {
                "query": "test query",
                "max_results": 10
            }
        }

    def test_get_test_data(self):
        """Test getting test data for a specific test"""
        self.manager.data = self.test_data
        test_data = self.manager.get_test_data("login_test")
        self.assertEqual(test_data["username"], "test_user")
        self.assertEqual(test_data["settings"]["timeout"], 30)

    def test_get_test_data_nonexistent(self):
        """Test getting test data for nonexistent test"""
        self.manager.data = self.test_data
        test_data = self.manager.get_test_data("nonexistent_test")
        self.assertEqual(test_data, {})

    def test_get_all_test_data(self):
        """Test getting all test data"""
        self.manager.data = self.test_data
        all_data = self.manager.get_all_test_data()
        self.assertEqual(all_data, self.test_data)

    @patch(
        'builtins.open',
        mock_open(
            read_data=yaml.dump({
                "login_test": {
                    "username": "test_user",
                    "password": "ENC[encrypted_password]"
                }
            })
        )
    )
    def test_load_data(self):
        """Test loading data from file"""
        with patch.object(SecretManager, 'decrypt', return_value='decrypted'):
            data = self.manager.load_data()
            self.assertIsInstance(data, dict)
            self.assertIn("login_test", data)
            self.assertEqual(data["login_test"]["username"], "test_user")
            self.assertEqual(data["login_test"]["password"], "decrypted")

    @patch('builtins.open', side_effect=FileNotFoundError)
    def test_load_data_file_not_found(self, _):
        """Test loading data when file not found"""
        with self.assertRaises(FileNotFoundError):
            self.manager.load_data()

    def test_process_secrets(self):
        """Test processing of encrypted secrets"""
        test_data = {
            "plain": "text",
            "secret": "ENC[encrypted]",
            "nested": {
                "secret": "ENC[nested_encrypted]"
            },
            "list": ["plain", "ENC[list_encrypted]"]
        }

        with patch.object(SecretManager, 'decrypt', return_value='decrypted'):
            processed = self.manager.process_secrets(test_data)
            self.assertEqual(processed["plain"], "text")
            self.assertEqual(processed["secret"], "decrypted")
            self.assertEqual(processed["nested"]["secret"], "decrypted")
            self.assertEqual(processed["list"][1], "decrypted")

    def test_process_secrets_no_encryption(self):
        """Test processing of data without encrypted values"""
        test_data = {
            "plain": "text",
            "nested": {
                "value": "plain"
            },
            "list": ["plain", "also_plain"]
        }

        processed = self.manager.process_secrets(test_data)
        self.assertEqual(processed, test_data)
