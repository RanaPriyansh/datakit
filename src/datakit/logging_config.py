"""
Logging configuration for datakit.

Provides structured logging with environment-based configuration.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Optional

import os


def setup_logging(
    level: Optional[str] = None,
    log_file: Optional[str] = None,
    json_format: bool = False
) -> logging.Logger:
    """
    Configure logging for datakit.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL). Defaults to DATATKIT_LOG_LEVEL env var or INFO.
        log_file: Optional file path to write logs to.
        json_format: If True, use JSON formatting (useful for log aggregation).

    Returns:
        Configured logger instance.
    """
    # Determine log level
    if level is None:
        level = os.getenv('DATATKIT_LOG_LEVEL', 'INFO').upper()
    numeric_level = getattr(logging, level, logging.INFO)

    # Create logger
    logger = logging.getLogger('datakit')
    logger.setLevel(numeric_level)

    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)

    if json_format:
        # Simple JSON format
        import json
        class JSONFormatter(logging.Formatter):
            def format(self, record):
                log_obj = {
                    'timestamp': self.formatTime(record, self.datefmt),
                    'level': record.levelname,
                    'name': record.name,
                    'message': record.getMessage(),
                }
                if record.exc_info:
                    log_obj['exc_info'] = self.formatException(record.exc_info)
                return json.dumps(log_obj)
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Optional file handler
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger() -> logging.Logger:
    """Get the datakit logger, setting up default configuration if needed."""
    return setup_logging()
