"""
datakit – Data format converter toolkit.
Convert, validate, filter, merge, and transform data between formats.
"""

__version__ = "1.0.0"

# Core classes
from .core import (
    DataConverter,
    DataValidator,
    DataFilter,
    DataMerger,
    DataSampler,
    Dataset,
)

# Agent API
from .agent import (
    convert,
    validate,
    filter_data,
    select,
    merge,
    summary,
    sample,
    infer_schema,
    get_agent_function,
    list_agent_functions,
    AGENT_FUNCTIONS,
)

# Exceptions
from .exceptions import (
    DatakitError,
    ValidationError,
    FormatError,
    FileOperationError,
    SchemaError,
)

# Logging
from .logging_config import setup_logging, get_logger

__all__ = [
    # Version
    "__version__",
    # Core
    "DataConverter",
    "DataValidator",
    "DataFilter",
    "DataMerger",
    "DataSampler",
    "Dataset",
    # Agent functions
    "convert",
    "validate",
    "filter_data",
    "select",
    "merge",
    "summary",
    "sample",
    "infer_schema",
    "get_agent_function",
    "list_agent_functions",
    "AGENT_FUNCTIONS",
    # Exceptions
    "DatakitError",
    "ValidationError",
    "FormatError",
    "FileOperationError",
    "SchemaError",
    # Logging
    "setup_logging",
    "get_logger",
]
