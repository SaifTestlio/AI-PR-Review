"""
This module contains test configuration and fixtures for pytest.
"""
from dataclasses import fields

import pytest

from lib.models import (
    AppiumProperties,
    BitbarOptions,
    ExecutionProperties,
    FrameworkProperties,
    SauceLabsOptions
)
from lib.types import (
    ApplicationType,
    PlatformType,
    ProviderType
)
from lib.utils.logger import setup_logger

def pytest_addoption(parser: pytest.Parser):
    """Add command line options for test configuration"""
    dataclass_types = {
        "execution_properties": ExecutionProperties,
        "framework_properties": FrameworkProperties,
        "appium_properties": AppiumProperties
    }

    added_options = set()
    logger = setup_logger()

    for dataclass_type in dataclass_types.values():
        instance = dataclass_type()
        for field in fields(dataclass_type):
            option_name = f"--{field.name}"
            if option_name not in added_options:
                default_value = getattr(instance, field.name)
                if field.type in (ApplicationType, ProviderType, PlatformType):
                    parser.addoption(
                        option_name,
                        action="store",
                        default=default_value.value,
                        choices=[t.value for t in field.type],
                    )
                    logger.info(
                        "Added option %s with default: %s", option_name, default_value.value
                    )
                else:
                    parser.addoption(
                        option_name, action="store", default=default_value, type=field.type
                    )
                    logger.info(
                        "Added option %s with default: %s", option_name, default_value
                    )
                added_options.add(option_name)

    bitbar_instance = BitbarOptions()
    for field in fields(BitbarOptions):
        option_name = f"--bitbar_{field.name}"
        if option_name not in added_options:
            default_value = getattr(bitbar_instance, field.name)
            parser.addoption(
                option_name, action="store", default=default_value, type=field.type
            )
            logger.info(
                "Added option %s with default: %s", option_name, default_value
            )
            added_options.add(option_name)

    saucelabs_instance = SauceLabsOptions()
    for field in fields(SauceLabsOptions):
        option_name = f"--saucelabs_{field.name}"
        if option_name not in added_options:
            default_value = getattr(saucelabs_instance, field.name)
            parser.addoption(
                option_name, action="store", default=default_value, type=field.type
            )
            logger.info(
                "Added option %s with default: %s", option_name, default_value
            )
            added_options.add(option_name)

def initialize_dataclass(dataclass_instance, request, prefix=""):
    """Helper function to initialize dataclass fields from pytest options"""
    if not hasattr(dataclass_instance, '__dataclass_fields__'):
        raise TypeError(f"{dataclass_instance} is not a dataclass instance")

    for field in fields(dataclass_instance):
        option_name = f"--{prefix}{field.name}" if prefix else f"--{field.name}"
        default_value = getattr(dataclass_instance, field.name, None)
        value = request.config.getoption(option_name, default_value)
        if field.type in (ApplicationType, ProviderType, PlatformType):
            value = field.type(value)
        setattr(dataclass_instance, field.name, value)

@pytest.fixture(scope="class")
def properties(request: pytest.FixtureRequest):
    """Pytest fixture that initializes and sets properties for test configuration"""
    dataclass_types = {
        "execution_properties": ExecutionProperties,
        "framework_properties": FrameworkProperties,
        "appium_properties": AppiumProperties
    }

    logger = setup_logger()
    for property_name, dataclass_type in dataclass_types.items():
        dataclass_instance = dataclass_type()
        initialize_dataclass(dataclass_instance, request)

        if property_name == "appium_properties":
            bitbar_instance = BitbarOptions()
            for field in fields(BitbarOptions):
                option_name = f"--bitbar_{field.name}"
                value = request.config.getoption(option_name)
                setattr(bitbar_instance, field.name, value)
            dataclass_instance.bitbar_options = bitbar_instance

            saucelabs_instance = SauceLabsOptions()
            for field in fields(SauceLabsOptions):
                option_name = f"--saucelabs_{field.name}"
                value = request.config.getoption(option_name)
                setattr(saucelabs_instance, field.name, value)
            dataclass_instance.saucelabs_options = saucelabs_instance

        setattr(request.cls, property_name, dataclass_instance)
        logger.info("Initialized %s with values: %s", property_name, dataclass_instance)

@pytest.mark.usefixtures("properties")
class TestProperties:
    """Test cases for properties fixture"""
    execution_properties: ExecutionProperties
    framework_properties: FrameworkProperties
    appium_properties: AppiumProperties

    def test_execution_properties_initialized(self):
        """Verify ExecutionProperties are correctly initialized"""
        assert hasattr(self, "execution_properties")
        assert isinstance(self.execution_properties, ExecutionProperties)
        assert hasattr(self.execution_properties, "application_type")
        assert isinstance(self.execution_properties.application_type, ApplicationType)
        assert hasattr(self.execution_properties, "provider")
        assert isinstance(self.execution_properties.provider, ProviderType)
        assert hasattr(self.execution_properties, "log_level")
        assert isinstance(self.execution_properties.log_level, str)
        assert hasattr(self.execution_properties, "test_grep")
        assert isinstance(self.execution_properties.test_grep, str)
        assert hasattr(self.execution_properties, "test_spec")
        assert isinstance(self.execution_properties.test_spec, str)

    def test_framework_properties_initialized(self):
        """Verify FrameworkProperties are correctly initialized"""
        assert hasattr(self, "framework_properties")
        assert isinstance(self.framework_properties, FrameworkProperties)
        assert hasattr(self.framework_properties, "path_attachments_dir")
        assert isinstance(self.framework_properties.path_attachments_dir, str)
        assert hasattr(self.framework_properties, "time_implicit_wait")
        assert isinstance(self.framework_properties.time_implicit_wait, float)
        assert hasattr(self.framework_properties, "time_timeout")
        assert isinstance(self.framework_properties.time_timeout, float)
        assert hasattr(self.framework_properties, "time_interval")
        assert isinstance(self.framework_properties.time_interval, float)

    def test_appium_properties_initialized(self):
        """Verify AppiumProperties are correctly initialized"""
        assert hasattr(self, "appium_properties")
        assert isinstance(self.appium_properties, AppiumProperties)
        assert hasattr(self.appium_properties, "platform")
        assert isinstance(self.appium_properties.platform, PlatformType)
        assert hasattr(self.appium_properties, "platform_version")
        assert isinstance(self.appium_properties.platform_version, str)
        assert hasattr(self.appium_properties, "url")
        assert isinstance(self.appium_properties.url, str)
        assert hasattr(self.appium_properties, "application_id")
        assert isinstance(self.appium_properties.application_id, str)
        assert hasattr(self.appium_properties, "application_launch_activity")
        assert isinstance(self.appium_properties.application_launch_activity, str)
        assert hasattr(self.appium_properties, "device_udid")
        assert isinstance(self.appium_properties.device_udid, str)
        assert hasattr(self.appium_properties, "device_name")
        assert isinstance(self.appium_properties.device_name, str)

        assert isinstance(self.appium_properties.bitbar_options, BitbarOptions)
        assert hasattr(self.appium_properties.bitbar_options, "api_key")
        assert isinstance(self.appium_properties.bitbar_options.api_key, str)
        assert hasattr(self.appium_properties.bitbar_options, "app_id")
        assert isinstance(self.appium_properties.bitbar_options.app_id, str)
        assert hasattr(self.appium_properties.bitbar_options, "project")
        assert isinstance(self.appium_properties.bitbar_options.project, str)
        assert hasattr(self.appium_properties.bitbar_options, "testrun")
        assert isinstance(self.appium_properties.bitbar_options.testrun, str)

        assert isinstance(self.appium_properties.saucelabs_options, SauceLabsOptions)
        assert hasattr(self.appium_properties.saucelabs_options, "name")
        assert isinstance(self.appium_properties.saucelabs_options.name, str)
        assert hasattr(self.appium_properties.saucelabs_options, "username")
        assert isinstance(self.appium_properties.saucelabs_options.username, str)
        assert hasattr(self.appium_properties.saucelabs_options, "access_key")
        assert isinstance(self.appium_properties.saucelabs_options.access_key, str)

#### abaskjfdjk###