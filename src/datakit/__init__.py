"""
datakit – Data format converter toolkit.
Convert, validate, filter, merge, and transform data between formats.
"""

__version__ = "1.0.0"
from .core import DataConverter, DataValidator, DataFilter, DataMerger
from .cli import main
