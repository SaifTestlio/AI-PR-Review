"""
Abstract base class for page objects in the test automation framework.

This class provides common functionality for all page objects including:
- Element finding and interaction methods with explicit waits
- Logging of element actions
- Locator management
- Driver and properties management

Key features:
- Explicit waits for element presence/visibility
- Logging of element interactions
- Platform-specific locator handling
- Common element actions (click, send keys, etc)
- Abstract base class pattern

Usage:
    class LoginPage(AbstractPage):
        def __init__(self, driver, properties):
            super().__init__(driver, properties)
            
        def login(self, username, password):
            self.send_keys(self.locator_manager.get_locator("login", "username"), username)
            self.send_keys(self.locator_manager.get_locator("login", "password"), password)
            self.click_element(self.locator_manager.get_locator("login", "submit"))
"""
from abc import ABC, abstractmethod

from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from lib.locators import LocatorManager
from lib.models import Properties
from lib.utils.logger import setup_logger

class AbstractPage(ABC):
    """Base abstract class for all page objects"""
    def __init__(
        self,
        driver: webdriver.Remote,
        screen: str,
        properties: Properties
    ):
        self.driver = driver
        self.properties = properties
        self.logger = setup_logger(properties.execution.log_level)
        self.locator_manager = LocatorManager(properties.webdriver.platform)
        self.locators = self.locator_manager.get_locators(screen)
        self.wait = WebDriverWait(
            driver=driver,
            timeout=properties.framework.time_timeout,
            poll_frequency=properties.framework.time_interval
        )

    def _log_element_action(self, action: str, locator: tuple[AppiumBy, str]):
        """Helper method to log element actions"""
        self.logger.info(
            "%s: %s with type: %s",
            action,
            locator[1],
            locator[0]
        )

    def _get_locator(self, key: str) -> tuple:
        """Helper method to get locator tuple"""
        return (self.locators[key]['type'], self.locators[key]['value'])

    def find_element(self, locator: tuple[AppiumBy, str]) -> WebElement:
        """Find element with explicit wait"""
        self._log_element_action("Finding element", locator)
        return self.wait.until(EC.presence_of_element_located(locator))

    def find_elements(self, locator: tuple[AppiumBy, str]) -> list[WebElement]:
        """Find elements with explicit wait"""
        self._log_element_action("Finding elements", locator)
        return self.wait.until(EC.presence_of_all_elements_located(locator))

    def click_element(self, locator: tuple[AppiumBy, str]):
        """Click element with explicit wait"""
        self._log_element_action("Clicking element", locator)
        self.wait.until(EC.element_to_be_clickable(locator)).click()

    def send_keys(self, locator: tuple[AppiumBy, str], text: str):
        """Send keys to element with explicit wait"""
        self._log_element_action("Sending keys to element", locator)
        element = self.find_element(locator)
        element.clear()
        element.send_keys(text)

    def get_text(self, locator: tuple[AppiumBy, str]) -> str:
        """Get text from element with explicit wait"""
        self._log_element_action("Getting text from element", locator)
        return self.find_element(locator).text

    def is_element_present(self, locator: tuple[AppiumBy, str]) -> bool:
        """Check if element is present"""
        self._log_element_action("Checking if element is present", locator)
        try:
            self.find_element(locator)
            return True
        except NoSuchElementException:
            self.logger.info(
                "Element %s not found.",
                locator[1]
            )
        except TimeoutException:
            self.logger.info(
                "An element couldn't be located after %s seconds.",
                self.properties.framework.time_timeout
            )
        return False

    def wait_for_element_visible(self, locator: tuple[AppiumBy, str]) -> WebElement | bool:
        """Wait for element to be visible"""
        self._log_element_action("Waiting for element to be visible", locator)
        return self.wait.until(EC.visibility_of_element_located(locator))

    def wait_for_element_invisible(self, locator: tuple[AppiumBy, str]) -> WebElement | bool:
        """Wait for element to be invisible"""
        self._log_element_action("Waiting for element to be invisible", locator)
        return self.wait.until(EC.invisibility_of_element_located(locator))

    @abstractmethod
    def is_page_loaded(self) -> bool:
        """Verify that page is loaded"""
