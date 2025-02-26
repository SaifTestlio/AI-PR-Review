"""
This module defines the core data models used throughout the test automation framework.
"""
from dataclasses import dataclass, field
from typing import NamedTuple

from lib.types import ApplicationType, PlatformType, ProviderType

@dataclass
class ExecutionProperties:
    """A dataclass that holds various configuration properties for tests"""
    application_type: ApplicationType = ApplicationType.WEB
    provider: ProviderType = ProviderType.LOCAL
    log_level: str = 'INFO'
    test_grep: str = ''
    test_spec: str = ''

@dataclass
class FrameworkProperties:
    """A dataclass that holds various configuration properties for tests"""
    encryption_key: str = 'm8e0EMDdBnV0I6SGz-H7v1CKgQhLSnNcEIS5K4-WD1o='
    path_attachments_dir: str = 'attachments'
    test_data_file: str = 'test_data.yml'
    time_implicit_wait: float = 10.0
    time_timeout: float = 10.0
    time_interval: float = 0.5

@dataclass
class WebDriverProperties:
    """A dataclass that holds various configuration properties for tests"""
    platform: PlatformType = PlatformType.WINDOWS
    platform_version: str = ''
    url: str = 'http://localhost:4723'

@dataclass
class BitbarOptions:
    """A dataclass that holds various configuration properties for tests"""
    api_key: str = ''
    app_id: str = ''
    project: str = ''
    testrun: str = ''

@dataclass
class SauceLabsOptions:
    """A dataclass that holds various configuration properties for tests"""
    name: str = ''
    username: str = ''
    access_key: str = ''

@dataclass
class AppiumProperties(WebDriverProperties):
    """A dataclass that holds various configuration properties for tests"""
    application_id: str = ''
    application_launch_activity: str = ''
    device_udid: str = ''
    device_name: str = ''
    bitbar_options: BitbarOptions = field(default_factory=BitbarOptions)
    saucelabs_options: SauceLabsOptions = field(default_factory=SauceLabsOptions)

class Properties(NamedTuple):
    """Properties model for the test automation framework"""
    execution: ExecutionProperties
    framework: FrameworkProperties
    webdriver: AppiumProperties
