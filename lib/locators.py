"""
This module provides locator management functionality for test automation.

The module handles:
- Loading and caching locators from YAML files
- Converting locator strings to Appium/Selenium locator tuples
- Platform-specific locator management
- Locator type enumeration and validation

Key features:
- YAML-based locator storage
- Platform-specific locator files
- Locator type validation and conversion
- Caching for performance
- Error handling for missing locators

Usage:
    manager = LocatorManager(PlatformType.ANDROID)
    locator = manager.get_locator("login_screen", "username_field")
"""

import os
import unittest
from enum import Enum
from unittest.mock import mock_open, patch

import yaml
from appium.webdriver.common.appiumby import AppiumBy

from tests.conftest import PlatformType

class LocatorType(Enum):
    """Enum for locator types"""
    ID = AppiumBy.ID
    NAME = AppiumBy.NAME
    CLASS_NAME = AppiumBy.CLASS_NAME
    TAG_NAME = AppiumBy.TAG_NAME
    XPATH = AppiumBy.XPATH
    CSS_SELECTOR = AppiumBy.CSS_SELECTOR
    LINK_TEXT = AppiumBy.LINK_TEXT
    PARTIAL_LINK_TEXT = AppiumBy.PARTIAL_LINK_TEXT
    ACCESSIBILITY_ID = AppiumBy.ACCESSIBILITY_ID
    IMAGE = AppiumBy.IMAGE
    ANDROID_DATA_MATCHER = AppiumBy.ANDROID_DATA_MATCHER
    ANDROID_UIAUTOMATOR = AppiumBy.ANDROID_UIAUTOMATOR
    ANDROID_VIEWTAG = AppiumBy.ANDROID_VIEWTAG
    IOS_CLASS_CHAIN = AppiumBy.IOS_CLASS_CHAIN
    IOS_PREDICATE = AppiumBy.IOS_PREDICATE
    CUSTOM = AppiumBy.CUSTOM

class LocatorManager:
    """Class to store and retrieve locators for different platforms"""
    def __init__(self, platform: PlatformType):
        self.platform = platform
        self._locators_cache = {}
        self._locators_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            f"locators_{platform.value.lower()}.yml"
        )

    def _load_locators(self) -> dict:
        """Loads locators from YAML file for the current platform"""
        try:
            with open(self._locators_file, encoding="utf-8") as f:
                return yaml.safe_load(f)
        except FileNotFoundError as exc:
            raise FileNotFoundError(
                f"Locators file for {self.platform.value} not found."
            ) from exc

    def get_locator(self, screen: str, element: str) -> tuple:
        """Gets a locator tuple (type, value) for a specific element on a screen"""
        if screen not in self._locators_cache:
            self._locators_cache[screen] = self._load_locators()

        try:
            locator_data = self._locators_cache[screen][element]
            return (
                LocatorType[locator_data["type"].upper()].value,
                locator_data["value"]
            )
        except KeyError as exc:
            raise KeyError(f"Element '{element}' not found in screen '{screen}'") from exc

    def get_locators(self, screen: str) -> dict:
        """Gets all locators for a specific screen"""
        if screen not in self._locators_cache:
            locators = self._load_locators()
            if screen not in locators:
                raise KeyError(f"Screen '{screen}' not found in locators")
            self._locators_cache[screen] = locators[screen]
        return self._locators_cache[screen]

    def set_locators(self, screen: str, locators: dict):
        """Sets locators for a screen in the cache"""
        self._locators_cache[screen] = locators

class TestPlatformLocatorManager(unittest.TestCase):
    """Test cases for PlatformLocatorManager class"""

    class TestablePlatformLocatorManager(LocatorManager):
        """Subclass to expose protected methods for testing"""
        def load_locators(self):
            """Expose protected method for testing"""
            return self._load_locators()

    def setUp(self):
        """Set up test fixtures"""
        self.manager = self.TestablePlatformLocatorManager(PlatformType.ANDROID)
        self.test_locators = {
            "login_screen": {
                "username": {
                    "type": "id",
                    "value": "username_field"
                },
                "password": {
                    "type": "xpath", 
                    "value": "//input[@type='password']"
                }
            }
        }

    def test_get_locator(self):
        """Test getting a locator"""
        self.manager.set_locators("login_screen", self.test_locators["login_screen"])
        locator = self.manager.get_locator("login_screen", "username")
        self.assertEqual(locator, ("id", "username_field"))

    def test_get_locator_invalid_screen(self):
        """Test getting a locator for invalid screen"""
        with self.assertRaises(KeyError):
            self.manager.get_locator("invalid_screen", "username")

    def test_get_locator_invalid_element(self):
        """Test getting a locator for invalid element"""
        self.manager.set_locators("login_screen", self.test_locators["login_screen"])
        with self.assertRaises(KeyError):
            self.manager.get_locator("login_screen", "invalid_element")

    def test_get_all_locators_for_screen(self):
        """Test getting all locators for a screen"""
        self.manager.set_locators("login_screen", self.test_locators["login_screen"])
        locators = self.manager.get_locators("login_screen")
        self.assertEqual(locators, self.test_locators["login_screen"])

    def test_get_all_locators_invalid_screen(self):
        """Test getting all locators for invalid screen"""
        with self.assertRaises(KeyError):
            self.manager.get_locators("invalid_screen")

    @patch(
        'builtins.open',
        mock_open(
            read_data=yaml.dump({
                "login_screen": {
                    "username": {
                        "type": "id",
                        "value": "test"
                    }
                }
            })
        )
    )
    def test_load_locators(self):
        """Test loading locators from file"""
        locators = self.manager.load_locators()
        self.assertIsInstance(locators, dict)
        self.assertIn("login_screen", locators)
        self.assertEqual(locators["login_screen"]["username"]["type"], "id")
        self.assertEqual(locators["login_screen"]["username"]["value"], "test")

    @patch('builtins.open', side_effect=FileNotFoundError)
    def test_load_locators_file_not_found(self, _):
        """Test loading locators when file not found"""
        with self.assertRaises(FileNotFoundError):
            self.manager.load_locators()
