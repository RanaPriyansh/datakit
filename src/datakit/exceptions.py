"""
Custom exceptions for datakit.

These provide clear, structured error handling for agent integration.
"""

from __future__ import annotations


class DatakitError(Exception):
    """Base exception for all datakit errors."""
    pass


class ValidationError(DatakitError):
    """Raised when data validation fails."""
    def __init__(self, message: str, errors: list[str] | None = None):
        super().__init__(message)
        self.errors = errors or []


class FormatError(DatakitError):
    """Raised when data format is unsupported or malformed."""
    pass


class FileOperationError(DatakitError):
    """Raised when file operations fail."""
    pass


class SchemaError(DatakitError):
    """Raised when schema operations fail."""
    pass
