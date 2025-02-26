"""
Base test module containing test configuration and base test case class.

This module provides:
- Base test case class with common setup/teardown functionality
- Driver initialization and management
- Test artifact capture (screenshots, logs, recordings)
- Platform-specific handling for Android/iOS

Key features:
- Automatic driver setup based on properties
- Test Flight app installation on iOS
- Screen recording capture
- Log and screenshot capture on test completion
- Platform-specific artifact handling

Usage:
    class LoginTests(BaseTestCase):
        def test_valid_login(self):
            # Test implementation
            pass

        def tearDown(self):
            self._capture_artifacts()
            super().tearDown()
"""
import unittest
from functools import wraps

import pytest
from selenium.common.exceptions import TimeoutException

from lib.data import DataManager
from lib.drivers import WebDriverFactory
from lib.models import PlatformType, ProviderType
from lib.utils.attachments import Attachments
from lib.utils.logger import setup_logger
from tests.conftest import (
    AppiumProperties,
    ExecutionProperties,
    FrameworkProperties
)

@pytest.mark.usefixtures('properties')
class BaseTestCase(unittest.TestCase):
    """Base test case class for all tests"""
    appium_properties: AppiumProperties
    execution_properties: ExecutionProperties
    framework_properties: FrameworkProperties
    test_data_manager: DataManager

    @staticmethod
    def handle_assertion_error(func):
        """Handle assertion errors"""
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except AssertionError as e:
                self.logger.error("Assertion failed in function %s: %s", func.__name__, str(e))
                self.capture_artifacts(include_screenshot=True)
                raise
        return wrapper

    @staticmethod
    def handle_timeout_error(func):
        """Handle timeout errors"""
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except TimeoutException as e:
                self.logger.error("Timeout error in function %s: %s", func.__name__, str(e))
                self.capture_artifacts(include_screenshot=True)
                raise
        return wrapper

    def setUp(self):
        """Set up test case with driver, logger and attachments"""
        super().setUp()

        self.test_data_manager = DataManager(self.framework_properties)
        self.driver = WebDriverFactory(self.execution_properties).create_driver(
            self.appium_properties
        )
        self.logger = setup_logger(self.execution_properties.log_level)
        self.attachments = Attachments(self.driver, self.framework_properties)

        self._start_recording()

    def _start_recording(self):
        """Start screen recording based on platform"""
        if self.appium_properties.platform == PlatformType.ANDROID:
            self.driver.execute_script('mobile: startMediaProjectionRecording')
        elif (
            self.appium_properties.platform == PlatformType.IOS and
            self.execution_properties.provider != ProviderType.SAUCELABS
        ):
            self.driver.start_recording_screen()

    def capture_artifacts(self, include_screenshot=False):
        """Capture test artifacts like logs and recordings"""
        platform = self.appium_properties.platform
        self.attachments.attach_logs(platform)
        self.attachments.attach_session_id()

        if self.execution_properties.provider != ProviderType.SAUCELABS:
            self.attachments.attach_recording(platform)

        if include_screenshot:
            self.attachments.attach_screenshot()

    def tearDown(self):
        """Clean up test case and capture artifacts"""
        self.capture_artifacts()
        if self.driver:
            self.driver.quit()
