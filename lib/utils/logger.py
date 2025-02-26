"""
This module provides logging functionality for the test automation framework.

The module handles:
- Setting up logging with configurable log levels
- Writing logs to timestamped files in a logs directory
- Formatting log messages with timestamps and log levels
- Testing logger initialization and formatting

Key features:
- Configurable log levels (INFO, DEBUG, etc)
- Automatic log file creation with timestamps
- Standard log message formatting
- Log directory management
- Unit tests for logger functionality

Usage:
    logger = setup_logger('DEBUG')
    logger.info('Info message')
    logger.debug('Debug message')
"""
import io
import logging
import os
from datetime import datetime
import pytest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
LOGS_DIR = os.path.join(PROJECT_ROOT, "logs")
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

os.makedirs(LOGS_DIR, exist_ok=True)
INITIAL_FILES = set(os.listdir(LOGS_DIR))

log_filename = os.path.join(LOGS_DIR, f"run-{datetime.now():%Y-%m-%d_%H-%M-%S}.log")

def setup_logger(log_level: str = 'INFO') -> logging.Logger:
    """Sets up a logger with a filename based on the current date and time"""
    logger = logging.getLogger(__name__)
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    handler = logging.FileHandler(log_filename)
    handler.setFormatter(logging.Formatter(fmt=LOG_FORMAT, datefmt=DATE_FORMAT))
    logger.addHandler(handler)
    return logger

class TestLogger:
    """Test class for the logger module"""
    @pytest.fixture
    def logger(self) -> logging.Logger:
        """Fixture to setup a logger instance"""
        return setup_logger()

    @pytest.fixture
    def stream_handler(self) -> tuple[logging.StreamHandler, io.StringIO]:
        """Fixture to setup a stream handler"""
        stream = io.StringIO()
        handler = logging.StreamHandler(stream)
        return handler, stream

    def test_logger_initialization(self, logger: logging.Logger):
        """Test that the logger is initialized correctly"""
        assert isinstance(logger, logging.Logger)
        assert logger.name == __name__
        assert os.path.exists(LOGS_DIR)
        assert os.path.isdir(LOGS_DIR)
        assert logger.level == logging.INFO
        assert len(logger.handlers) == 1
        handler = logger.handlers[0]
        assert isinstance(handler, logging.FileHandler)
        assert isinstance(handler.formatter, logging.Formatter)

    def test_logger_formatting(
            self,
            logger: logging.Logger,
            stream_handler: tuple[logging.StreamHandler, io.StringIO]
    ):
        """Test that the logger formats messages correctly"""
        handler, stream = stream_handler
        handler.setFormatter(logger.handlers[0].formatter)
        logger.addHandler(handler)
        test_message = 'Test log message'
        logger.info(test_message)
        log_output = stream.getvalue()
        assert test_message in log_output
        assert 'INFO' in log_output
        assert datetime.now().strftime('%Y-%m-%d') in log_output
        assert ' - ' in log_output
        logger.removeHandler(handler)
        stream.close()

    def test_logger_file_output(self, logger: logging.Logger):
        """Test that the logger writes messages to a file"""
        test_message = 'Test file output message'
        logger.info(test_message)
        current_files = set(os.listdir(LOGS_DIR))
        new_files = current_files - INITIAL_FILES
        assert len(new_files) == 1
        log_file = os.path.join(LOGS_DIR, list(new_files)[0])
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()
            assert test_message in content
            assert 'INFO' in content
            assert datetime.now().strftime('%Y-%m-%d') in content

    @pytest.mark.parametrize("level_name,level_value", [
        ('DEBUG', logging.DEBUG),
        ('INFO', logging.INFO),
        ('WARNING', logging.WARNING), 
        ('ERROR', logging.ERROR),
        ('CRITICAL', logging.CRITICAL)
    ])
    def test_logger_levels(self, level_name: str, level_value: int):
        """Test that the logger levels are set correctly"""
        logger = setup_logger(level_name)
        assert logger.level == level_value

    def test_invalid_level_defaults_to_info(self):
        """Test that an invalid level defaults to INFO"""
        logger = setup_logger('INVALID_LEVEL')
        assert logger.level == logging.INFO

    def test_logger_message_filtering(
            self,
            stream_handler: tuple[logging.StreamHandler, io.StringIO]
    ):
        """Test that the logger filters messages based on level"""
        logger = setup_logger('INFO')
        handler, stream = stream_handler
        handler.setFormatter(logger.handlers[0].formatter)
        logger.addHandler(handler)
        logger.debug('Debug message')
        assert stream.getvalue() == ''
        logger.info('Info message')
        assert 'Info message' in stream.getvalue()
        logger.removeHandler(handler)
        stream.close()

    def test_logger_error_handling(self, logger: logging.Logger):
        """Test that the logger handles different message types correctly"""
        test_messages: list[object] = [None, '', 123, ['test'], {'key': 'value'}]
        for msg in test_messages:
            logger.info(msg)
        logger.info('Normal message')
