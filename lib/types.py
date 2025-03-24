"""
This module defines the core enums used throughout the test automation framework.

The module contains enums for:
- ApplicationType: Defines the type of application being tested (web, mobile native, mobile web)
- PlatformType: Defines the platform/OS being tested on (Android, iOS, Linux, Mac, Windows) 
- ProviderType: Defines the test execution provider (Bitbar, Local, Saucelabs)

These enums are used for configuration and to control test execution behavior based on
the target environment and application type.

Usage:
    from lib.types import ApplicationType, PlatformType, ProviderType
    
    app_type = ApplicationType.WEB
    platform = PlatformType.ANDROID
    provider = ProviderType.LOCAL
"""
from enum import Enum

class ApplicationType(Enum):
    """Enum for application types"""
    WEB = 'web'
    MOBILE_NATIVE = 'mobile-native'
    MOBILE_WEB = 'mobile-web'

class PlatformType(Enum):
    """Enum for platform types"""
    ANDROID = 'android'
    IOS = 'ios'
    LINUX = 'linux'
    MAC = 'mac'
    WINDOWS = 'windows'

class ProviderType(Enum):
    """Enum for provider types"""
    BITBAR = 'bitbar'
    LOCAL = 'local'
    SAUCELABS = 'saucelabs'

class ProviderType(Enum):
    """Enum for provider types"""
    BITBAR = 'test'
    LOCAL = 'test'
    SAUCELABS = 'test'
