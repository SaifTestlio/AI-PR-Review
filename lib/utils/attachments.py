"""
This module provides functionality for attaching test artifacts to Allure reports.

The Attachments class handles:
- Capturing and saving screenshots during test execution
- Recording and saving screen recordings for Android and iOS
- Collecting and saving device logs (logcat for Android, system logs for iOS)
- Attaching all captured artifacts to Allure test reports

Key features:
- Platform-specific handling for Android and iOS
- Automatic file naming with timestamps
- Integration with Allure reporting framework
- Support for screenshots, recordings and logs
"""
import base64
import os
from datetime import datetime
from typing import Callable

import allure
from appium import webdriver

from lib.models import FrameworkProperties, PlatformType

class Attachments:
    """Class for attaching files to Allure reports"""
    TEXT_EXT = 'txt'
    MP4_EXT = 'mp4'
    PNG_EXT = 'png'

    def __init__(self, driver: webdriver.Remote, framework_properties: FrameworkProperties):
        self.driver = driver
        self.framework_properties = framework_properties
        self.timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        self.attachments_dir = os.path.join(
            os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")),
            self.framework_properties.path_attachments_dir
        )
        os.makedirs(self.attachments_dir, exist_ok=True)

        self._log_handlers = {
            PlatformType.ANDROID: lambda: self._save_logs('logcat'),
            PlatformType.IOS: lambda: self._save_logs('syslog')
        }

        self._recording_handlers = {
            PlatformType.ANDROID:
                lambda: self._save_recording('mobile: stopMediaProjectionRecording'),
            PlatformType.IOS:
                lambda: self._save_file(
                    base64.b64decode(self.driver.stop_recording_screen()),
                    'recording',
                    self.MP4_EXT
                )
        }

    def _save_file(self, content: bytes, file_type: str, extension: str) -> str:
        """Generic method to save file content"""
        filename = os.path.join(self.attachments_dir, f"{file_type}-{self.timestamp}.{extension}")
        with open(filename, 'wb') as f:
            f.write(content)
        return filename

    def _save_logs(self, log_type: str) -> str:
        """Save logs to a file"""
        logs = self.driver.get_log(log_type)
        content = "\n".join(f"{log['timestamp']} {log['message']}" for log in logs)
        return self._save_file(content.encode('utf-8'), log_type, self.TEXT_EXT)

    def _save_recording(self, command: str) -> str:
        """Save the screen recording to a file"""
        recording = self.driver.execute_script(command)
        return self._save_file(base64.b64decode(recording), 'recording', self.MP4_EXT)

    def _attach_file(self, save_func: Callable, name: str, attachment_type: allure.attachment_type):
        """Generic method to attach file to Allure report"""
        filename = save_func()
        allure.attach.file(filename, name=name, attachment_type=attachment_type)

    def attach_logs(self, platform: PlatformType):
        """Attach logs to the Allure report"""
        self._attach_file(
            self._log_handlers[platform],
            'logs',
            allure.attachment_type.TEXT
        )

    def attach_recording(self, platform: PlatformType):
        """Attach the recording to the Allure report"""
        self._attach_file(
            self._recording_handlers[platform],
            'recording',
            allure.attachment_type.MP4
        )

    def attach_screenshot(self):
        """Attach the screenshot to the Allure report"""
        self._attach_file(
            lambda: self._save_file(
                self.driver.get_screenshot_as_png(),
                'screenshot',
                self.PNG_EXT
            ),
            'screenshot',
            allure.attachment_type.PNG
        )

    def attach_session_id(self):
        """Attach the WebDriver session ID to the Allure report"""
        self._attach_file(
            lambda: self._save_file(
                self.driver.session_id.encode('utf-8'),
                'session_id',
                self.TEXT_EXT
            ),
            'session_id',
            allure.attachment_type.TEXT
        )
