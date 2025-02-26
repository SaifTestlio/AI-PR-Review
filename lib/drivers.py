"""
This module provides WebDriver implementations for different platforms and providers.

The module handles:
- Abstract WebDriver base class defining the interface
- Concrete implementations for Android and iOS drivers
- Local and remote driver configurations
- Driver initialization with platform-specific options

Key features:
- Support for Android (UiAutomator2) and iOS (XCUITest) platforms
- Local and remote (cloud provider) driver configurations
- Property-based driver configuration
- Type-safe driver initialization

Usage:
    properties = AppiumProperties(...)
    driver = LocalAndroidWebDriver(properties)
    driver_instance = driver.get_driver()
"""
from abc import ABC, abstractmethod
from typing import cast

import pytest
from appium import webdriver as appium_webdriver
from appium.options.android import UiAutomator2Options
from appium.options.ios import XCUITestOptions
from appium.webdriver.appium_connection import AppiumConnection
from selenium.webdriver.remote.client_config import ClientConfig
from tests.conftest import (
    ApplicationType,
    AppiumProperties,
    ExecutionProperties,
    PlatformType,
    ProviderType
)

class WebDriver(ABC):
    """Abstract class representing a web driver"""
    def __init__(self, properties: AppiumProperties):
        self.properties = properties

    @abstractmethod
    def get_driver(self) -> appium_webdriver.Remote:
        """Abstract method to get the driver instance"""

    def get_properties(self) -> AppiumProperties:
        """Returns the properties instance"""
        return self.properties

class LocalAndroidWebDriver(WebDriver):
    """Class representing a local Android web driver"""
    def get_driver(self) -> appium_webdriver.Remote:
        options = UiAutomator2Options()
        options.udid = self.properties.device_udid
        options.platform_version = self.properties.platform_version
        options.app_package = self.properties.application_id
        options.app_activity = self.properties.application_launch_activity
        client_config = ClientConfig(remote_server_addr=self.properties.url)
        appium_executor = AppiumConnection(client_config=client_config)
        return appium_webdriver.Remote(
            command_executor=appium_executor,
            options=options
        )

class LocalIOSWebDriver(WebDriver):
    """Class representing a local iOS web driver"""
    def get_driver(self) -> appium_webdriver.Remote:
        options = XCUITestOptions()
        options.udid = self.properties.device_udid
        options.platform_version = self.properties.platform_version
        options.bundle_id = self.properties.application_id
        client_config = ClientConfig(remote_server_addr=self.properties.url)
        appium_executor = AppiumConnection(client_config=client_config)
        return appium_webdriver.Remote(
            command_executor=appium_executor,
            options=options
        )

class RemoteBitBarWebDriver(WebDriver):
    """Class representing a remote BitBar web driver"""
    def get_driver(self) -> appium_webdriver.Remote:
        options = UiAutomator2Options()
        options.app_package = self.properties.application_id
        options.app_activity = self.properties.application_launch_activity
        options.set_capability('bitbar:options', {
            'project': self.properties.bitbar_options.project,
            'testrun': self.properties.bitbar_options.testrun,
            'app': self.properties.bitbar_options.app_id,
            'apiKey': self.properties.bitbar_options.api_key,
            'device': self.properties.device_name,
            'findDevice': False,
            'appiumVersion': '2.1'
        })
        client_config = ClientConfig(remote_server_addr=self.properties.url)
        appium_executor = AppiumConnection(client_config=client_config)
        return appium_webdriver.Remote(
            command_executor=appium_executor,
            options=options
        )

class RemoteSauceWebDriver(WebDriver):
    """Class representing a remote Sauce web driver"""
    def get_driver(self) -> appium_webdriver.Remote:
        options = XCUITestOptions()
        options.device_name = self.properties.device_name
        options.platform_version = self.properties.platform_version
        options.set_capability('sauce:options', {
            'appiumVersion': 'latest',
            'name': self.properties.saucelabs_options.name,
            'username': self.properties.saucelabs_options.username,
            'accessKey': self.properties.saucelabs_options.access_key
        })
        client_config = ClientConfig(remote_server_addr=self.properties.url)
        appium_executor = AppiumConnection(client_config=client_config)
        return appium_webdriver.Remote(
            command_executor=appium_executor,
            options=options
        )

class WebDriverFactory:
    """Class representing a web driver factory"""
    def __init__(self, execution_properties: ExecutionProperties):
        self.execution_properties = execution_properties
        self.driver_classes = {}

        self.register_driver(
            ApplicationType.MOBILE_NATIVE,
            PlatformType.ANDROID,
            ProviderType.LOCAL,
            LocalAndroidWebDriver
        )
        self.register_driver(
            ApplicationType.MOBILE_NATIVE,
            PlatformType.IOS,
            ProviderType.LOCAL,
            LocalIOSWebDriver
        )
        self.register_driver(
            ApplicationType.MOBILE_NATIVE,
            PlatformType.ANDROID,
            ProviderType.BITBAR,
            RemoteBitBarWebDriver
        )
        self.register_driver(
            ApplicationType.MOBILE_NATIVE,
            PlatformType.IOS,
            ProviderType.SAUCELABS,
            RemoteSauceWebDriver
        )

    def register_driver(
        self,
        app_type: ApplicationType,
        driver_key: PlatformType,
        provider: ProviderType,
        driver_class: WebDriver
    ):
        """Registers a driver class for a given application type and driver key"""
        self.driver_classes[(app_type, driver_key, provider)] = driver_class

    def create_driver(
        self,
        properties: AppiumProperties
    ) -> appium_webdriver.Remote:
        """Method to create the driver instance"""
        app_type = self.execution_properties.application_type
        provider = self.execution_properties.provider

        if app_type != ApplicationType.MOBILE_NATIVE:
            raise ValueError(f"Unsupported application type: {app_type}")

        properties = cast(AppiumProperties, properties)
        key = (app_type, properties.platform, provider)

        driver_class = self.driver_classes.get(key)
        if driver_class:
            return driver_class(properties).get_driver()

        if provider not in (ProviderType.LOCAL, ProviderType.BITBAR):
            raise NotImplementedError(f"{provider.name} provider not implemented")

        raise ValueError(f"Unsupported platform: {properties.platform}")

class TestWebDriverFactory:
    """Test cases for WebDriverFactory class"""
    @pytest.fixture
    def setup(self):
        """Setup test fixtures"""
        execution_props = ExecutionProperties()
        factory = WebDriverFactory(execution_props)
        appium_props = AppiumProperties()
        return factory, appium_props

    def test_create_driver_unsupported_platform(self, setup):
        """Test create_driver raises error for unsupported platform"""
        factory, appium_props = setup
        factory.execution_properties.application_type = ApplicationType.MOBILE_NATIVE
        appium_props.platform = "unsupported"

        with pytest.raises(ValueError) as exc_info:
            factory.create_driver(appium_props)
        assert "Unsupported platform" in str(exc_info.value)

    def test_create_driver_unsupported_application_type(self, setup):
        """Test create_driver raises error for unsupported application type"""
        factory, appium_props = setup
        factory.execution_properties.application_type = "unsupported"

        with pytest.raises(ValueError) as exc_info:
            factory.create_driver(appium_props)
        assert "Unsupported application type" in str(exc_info.value)
