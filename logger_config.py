"""
Logging Configuration for Voice Command AI System

This module provides centralized logging configuration with:
- Rotating file handlers (prevents disk fill-up)
- Multiple log files for different components
- Console output for real-time monitoring
- Different log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Timestamped entries
- Automatic log directory creation

Usage:
    from logger_config import setup_logger
    
    logger = setup_logger('intent_os')
    logger.info("System started")
    logger.error("Something went wrong")
"""

import logging
import logging.handlers
import os
from pathlib import Path
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for console output"""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    def format(self, record):
        # Add color to levelname
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"
        
        return super().format(record)


def setup_logger(
    name: str,
    log_file: Optional[str] = None,
    level: int = logging.INFO,
    console: bool = True,
    max_bytes: int = 10 * 1024 * 1024,  # 10 MB
    backup_count: int = 5
) -> logging.Logger:
    """
    Setup a logger with file and console handlers
    
    Args:
        name: Logger name (usually module name)
        log_file: Log file name (optional, defaults to <name>.log)
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        console: Whether to output to console
        max_bytes: Maximum size of each log file before rotation
        backup_count: Number of backup log files to keep
    
    Returns:
        Configured logger instance
    """
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Determine log file name
    if log_file is None:
        log_file = f"{name}.log"
    
    log_path = log_dir / log_file
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        log_path,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(level)
    
    # File formatter (detailed)
    file_formatter = logging.Formatter(
        '%(asctime)s | %(name)s | %(levelname)s | %(funcName)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Console handler (if enabled)
    if console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        
        # Console formatter (simpler, with colors)
        console_formatter = ColoredFormatter(
            '%(levelname)s | %(name)s | %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    return logger


def setup_error_logger() -> logging.Logger:
    """
    Setup a special logger that captures all errors across the system
    
    Returns:
        Error logger instance
    """
    error_logger = logging.getLogger('error')
    error_logger.setLevel(logging.ERROR)
    
    # Avoid duplicate handlers
    if error_logger.handlers:
        return error_logger
    
    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Error file handler
    error_handler = logging.handlers.RotatingFileHandler(
        log_dir / "error.log",
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=10,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    
    # Detailed formatter for errors
    error_formatter = logging.Formatter(
        '%(asctime)s | %(name)s | %(levelname)s | %(pathname)s:%(lineno)d\n'
        '%(message)s\n'
        '----------------------------------------',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    error_handler.setFormatter(error_formatter)
    error_logger.addHandler(error_handler)
    
    return error_logger


def get_logger(name: str) -> logging.Logger:
    """
    Get or create a logger with default configuration
    
    Args:
        name: Logger name
    
    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)
    
    # If not configured yet, set it up
    if not logger.handlers:
        return setup_logger(name)
    
    return logger


# Pre-configured loggers for main components
def get_main_logger() -> logging.Logger:
    """Get logger for main.py"""
    return setup_logger('main', console=True)


def get_intent_os_logger() -> logging.Logger:
    """Get logger for Intent_OS.py"""
    return setup_logger('intent_os', console=True)


def get_classifier_logger() -> logging.Logger:
    """Get logger for Intent_classifier.py"""
    return setup_logger('classifier', console=True)


def get_api_logger() -> logging.Logger:
    """Get logger for api_handler.py"""
    return setup_logger('api', console=True)


def get_file_ops_logger() -> logging.Logger:
    """Get logger for file operations"""
    return setup_logger('file_ops', console=True)


def get_observer_logger() -> logging.Logger:
    """Get logger for Observer tracking"""
    return setup_logger('observer', log_file='observer.log', console=True)


# Initialize error logger
_error_logger = setup_error_logger()


def log_error(message: str, exc_info: bool = True):
    """
    Log an error to the error log
    
    Args:
        message: Error message
        exc_info: Include exception traceback
    """
    _error_logger.error(message, exc_info=exc_info)


# Example usage and testing
if __name__ == "__main__":
    print("=" * 60)
    print("LOGGING SYSTEM TEST")
    print("=" * 60)
    
    # Test different loggers
    main_log = get_main_logger()
    intent_log = get_intent_os_logger()
    classifier_log = get_classifier_logger()
    api_log = get_api_logger()
    
    # Test different log levels
    main_log.debug("Debug message - detailed info")
    main_log.info("Info message - general info")
    main_log.warning("Warning message - something to watch")
    main_log.error("Error message - something went wrong")
    
    intent_log.info("Intent OS initialized")
    classifier_log.info("Classified intent: search_web")
    api_log.info("API call successful")
    
    # Test error logging
    try:
        raise ValueError("Test error for logging")
    except Exception as e:
        log_error("Test error occurred")
    
    print("\n" + "=" * 60)
    print("✅ Logging system test complete!")
    print("📁 Check the 'logs/' directory for log files")
    print("=" * 60)
