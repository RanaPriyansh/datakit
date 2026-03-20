"""
Agent-friendly API wrapper for datakit.

Provides simplified functions that AI agents can call directly,
with structured inputs/outputs and JSON schema definitions for function calling.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from .core import DataConverter, DataFilter, DataMerger, DataSampler, DataValidator
from .exceptions import DatakitError, FileOperationError, ValidationError
from .logging_config import get_logger

logger = get_logger()


# ============== JSON Schemas for Function Calling ==============

CONVERT_SCHEMA = {
    "type": "object",
    "properties": {
        "input_path": {
            "type": "string",
            "description": "Path to input data file"
        },
        "output_path": {
            "type": "string",
            "description": "Path where output should be saved"
        },
        "input_format": {
            "type": "string",
            "enum": ["csv", "json", "yaml", "yml", "toml", "xml", "parquet", "excel", "xlsx", "xls"],
            "description": "Input format (auto-detected if omitted)"
        },
        "output_format": {
            "type": "string",
            "enum": ["csv", "json", "yaml", "yml", "toml", "xml", "parquet", "excel", "xlsx", "xls"],
            "description": "Output format (auto-detected from output_path if omitted)"
        }
    },
    "required": ["input_path", "output_path"],
    "additionalProperties": False
}

VALIDATE_SCHEMA = {
    "type": "object",
    "properties": {
        "input_path": {
            "type": "string",
            "description": "Path to data file to validate"
        },
        "schema": {
            "type": "object",
            "description": "Schema definition (field -> type mapping). Types: string, number, boolean, array, object. Omit to auto-infer."
        },
        "schema_path": {
            "type": "string",
            "description": "Path to schema file (JSON or YAML). Alternative to inline schema."
        },
        "output_format": {
            "type": "string",
            "enum": ["json", "text"],
            "description": "Output format for validation results"
        }
    },
    "required": ["input_path"],
    "additionalProperties": False
}

FILTER_SCHEMA = {
    "type": "object",
    "properties": {
        "input_path": {
            "type": "string",
            "description": "Path to input data file"
        },
        "conditions": {
            "type": "object",
            "description": "Filter conditions as JSON object. Example: {\"age\": {\"gt\": 18}, \"status\": \"active\"}"
        },
        "output_path": {
            "type": "string",
            "description": "Optional output file path"
        },
        "output_format": {
            "type": "string",
            "enum": ["json", "text"],
            "description": "How to output results"
        }
    },
    "required": ["input_path", "conditions"],
    "additionalProperties": False
}

SELECT_SCHEMA = {
    "type": "object",
    "properties": {
        "input_path": {
            "type": "string",
            "description": "Path to input data file"
        },
        "fields": {
            "type": "array",
            "items": {"type": "string"},
            "description": "List of field names to keep"
        },
        "output_path": {
            "type": "string",
            "description": "Optional output file path"
        },
        "output_format": {
            "type": "string",
            "enum": ["json", "text"],
            "description": "How to output results"
        }
    },
    "required": ["input_path", "fields"],
    "additionalProperties": False
}

MERGE_SCHEMA = {
    "type": "object",
    "properties": {
        "input1_path": {
            "type": "string",
            "description": "Path to first dataset"
        },
        "input2_path": {
            "type": "string",
            "description": "Path to second dataset"
        },
        "on": {
            "type": "string",
            "description": "Field to merge on (join key). If omitted, concatenates datasets."
        },
        "how": {
            "type": "string",
            "enum": ["inner", "left", "right", "outer"],
            "description": "Join type. Default: outer"
        },
        "output_path": {
            "type": "string",
            "description": "Output file path"
        }
    },
    "required": ["input1_path", "input2_path"],
    "additionalProperties": False
}

SUMMARY_SCHEMA = {
    "type": "object",
    "properties": {
        "input_path": {
            "type": "string",
            "description": "Path to data file"
        },
        "output_format": {
            "type": "string",
            "enum": ["json", "text"],
            "description": "Output format"
        }
    },
    "required": ["input_path"],
    "additionalProperties": False
}

SAMPLE_SCHEMA = {
    "type": "object",
    "properties": {
        "input_path": {
            "type": "string",
            "description": "Path to data file"
        },
        "n": {
            "type": "integer",
            "minimum": 1,
            "description": "Number of samples to return. Default: 10"
        },
        "method": {
            "type": "string",
            "enum": ["random", "first", "last"],
            "description": "Sampling method. Default: random"
        },
        "output_path": {
            "type": "string",
            "description": "Optional output file"
        }
    },
    "required": ["input_path"],
    "additionalProperties": False
}

INFER_SCHEMA_SCHEMA = {
    "type": "object",
    "properties": {
        "input_path": {
            "type": "string",
            "description": "Path to data file"
        },
        "output_path": {
            "type": "string",
            "description": "Optional: path to save schema"
        },
        "output_format": {
            "type": "string",
            "enum": ["json", "yaml", "text"],
            "description": "Output format for schema"
        }
    },
    "required": ["input_path"],
    "additionalProperties": False
}


# ============== Agent Functions ==============

def convert(input_path: str, output_path: str, **kwargs) -> Dict[str, Any]:
    """
    Convert data from one format to another.

    Args:
        input_path: Path to input file
        output_path: Path for output file
        **kwargs: input_format, output_format

    Returns:
        Dictionary with result status and metadata
    """
    try:
        result_path = DataConverter.convert(
            input_path,
            output_path,
            input_format=kwargs.get('input_format'),
            output_format=kwargs.get('output_format')
        )
        logger.info(f"Converted {input_path} to {result_path}")
        return {
            "success": True,
            "output_path": result_path,
            "input_path": input_path,
            "message": f"Successfully converted to {output_path}"
        }
    except Exception as e:
        logger.error(f"Convert failed: {e}")
        raise FileOperationError(f"Conversion failed: {e}") from e


def validate(input_path: str, schema: Optional[Dict[str, str]] = None,
             schema_path: Optional[str] = None, output_format: str = "text") -> Dict[str, Any]:
    """
    Validate data against a schema.

    Args:
        input_path: Path to data file
        schema: Optional inline schema definition
        schema_path: Optional path to schema file
        output_format: 'json' or 'text'

    Returns:
        Validation results dictionary
    """
    try:
        dataset = DataConverter.load(input_path)

        # Load schema
        if schema_path:
            schema_file = Path(schema_path)
            if schema_file.suffix == '.json':
                with open(schema_file) as f:
                    schema = json.load(f)
            elif schema_file.suffix in ['.yaml', '.yml']:
                import yaml
                with open(schema_file) as f:
                    schema = yaml.safe_load(f)
            else:
                raise ValueError(f"Unsupported schema format: {schema_file.suffix}")
        elif not schema:
            # Auto-infer
            schema = DataValidator.infer_schema(dataset.as_dicts)

        result = DataValidator.validate_schema(dataset.as_dicts, schema)

        logger.info(f"Validation completed: {result['valid']}, {len(result['errors'])} errors")
        return {
            "success": True,
            "valid": result['valid'],
            "errors": result['errors'][:100],  # Limit errors
            "warnings": result.get('warnings', []),
            "records_checked": result['records_checked'],
            "schema": schema
        }
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        raise ValidationError(f"Validation failed: {e}") from e


def filter_data(input_path: str, conditions: Dict[str, Any],
                output_path: Optional[str] = None,
                output_format: str = "json") -> Dict[str, Any]:
    """
    Filter data by conditions.

    Args:
        input_path: Path to input file
        conditions: Filter conditions (e.g., {"age": {"gt": 18}})
        output_path: Optional output file
        output_format: How to return results

    Returns:
        Filtered data or status
    """
    try:
        dataset = DataConverter.load(input_path)
        filtered = DataFilter.filter(dataset.as_dicts, conditions)

        if output_path:
            dataset.data = filtered
            DataConverter.save(dataset, output_path)
            logger.info(f"Filtered {len(filtered)} records to {output_path}")
            return {
                "success": True,
                "output_path": output_path,
                "records_filtered": len(filtered),
                "total_records": len(dataset.as_dicts)
            }
        else:
            logger.info(f"Filtered result: {len(filtered)} records")
            return {
                "success": True,
                "data": filtered[:1000],  # Limit for agent consumption
                "records_filtered": len(filtered),
                "total_records": len(dataset.as_dicts),
                "truncated": len(filtered) > 1000
            }
    except Exception as e:
        logger.error(f"Filter failed: {e}")
        raise DatakitError(f"Filter operation failed: {e}") from e


def select(input_path: str, fields: List[str],
           output_path: Optional[str] = None,
           output_format: str = "json") -> Dict[str, Any]:
    """
    Select specific fields from data.

    Args:
        input_path: Path to input file
        fields: List of field names to retain
        output_path: Optional output file
        output_format: Output format

    Returns:
        Selected data or status
    """
    try:
        dataset = DataConverter.load(input_path)
        selected = DataFilter.select(dataset.as_dicts, fields)

        if output_path:
            dataset.data = selected
            DataConverter.save(dataset, output_path)
            logger.info(f"Selected {len(fields)} fields, saved to {output_path}")
            return {
                "success": True,
                "output_path": output_path,
                "records": len(selected),
                "fields": fields
            }
        else:
            return {
                "success": True,
                "data": selected[:1000],
                "records": len(selected),
                "fields": fields,
                "truncated": len(selected) > 1000
            }
    except Exception as e:
        logger.error(f"Select failed: {e}")
        raise DatakitError(f"Select operation failed: {e}") from e


def merge(input1_path: str, input2_path: str, on: Optional[str] = None,
          how: str = "outer", output_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Merge two datasets.

    Args:
        input1_path: First dataset path
        input2_path: Second dataset path
        on: Join key field (if None, concatenates)
        how: Join type: inner, left, right, outer
        output_path: Optional output file

    Returns:
        Merged data or status
    """
    try:
        dataset1 = DataConverter.load(input1_path)
        dataset2 = DataConverter.load(input2_path)

        merged = DataMerger.merge(
            dataset1.as_dicts,
            dataset2.as_dicts,
            on=on,
            how=how
        )

        if output_path:
            dataset1.data = merged
            DataConverter.save(dataset1, output_path)
            logger.info(f"Merged {len(merged)} records to {output_path}")
            return {
                "success": True,
                "output_path": output_path,
                "records": len(merged),
                "how": how
            }
        else:
            return {
                "success": True,
                "data": merged[:1000],
                "records": len(merged),
                "how": how,
                "truncated": len(merged) > 1000
            }
    except Exception as e:
        logger.error(f"Merge failed: {e}")
        raise DatakitError(f"Merge operation failed: {e}") from e


def summary(input_path: str, output_format: str = "text") -> Dict[str, Any]:
    """
    Generate dataset summary.

    Args:
        input_path: Path to data file
        output_format: 'json' or 'text'

    Returns:
        Summary statistics
    """
    try:
        dataset = DataConverter.load(input_path)
        summary = DataSampler.summary(dataset.as_dicts)

        logger.info(f"Generated summary for {input_path}")
        return {
            "success": True,
            "summary": summary,
            "file": input_path
        }
    except Exception as e:
        logger.error(f"Summary failed: {e}")
        raise DatakitError(f"Summary failed: {e}") from e


def sample(input_path: str, n: int = 10, method: str = "random",
           output_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Sample records from dataset.

    Args:
        input_path: Path to data file
        n: Number of samples
        method: 'random', 'first', 'last'
        output_path: Optional output file

    Returns:
        Sampled data or status
    """
    try:
        dataset = DataConverter.load(input_path)
        sampled = DataSampler.sample(dataset.as_dicts, n=n, method=method)

        if output_path:
            dataset.data = sampled
            DataConverter.save(dataset, output_path)
            logger.info(f"Sampled {len(sampled)} records to {output_path}")
            return {
                "success": True,
                "output_path": output_path,
                "records": len(sampled),
                "method": method
            }
        else:
            return {
                "success": True,
                "data": sampled,
                "records": len(sampled),
                "method": method
            }
    except Exception as e:
        logger.error(f"Sample failed: {e}")
        raise DatakitError(f"Sample failed: {e}") from e


def infer_schema(input_path: str, output_path: Optional[str] = None,
                 output_format: str = "text") -> Dict[str, Any]:
    """
    Infer schema from data.

    Args:
        input_path: Path to data file
        output_path: Optional path to save schema
        output_format: 'json', 'yaml', or 'text'

    Returns:
        Inferred schema
    """
    try:
        dataset = DataConverter.load(input_path)
        schema = DataValidator.infer_schema(dataset.as_dicts)

        if output_path:
            schema_file = Path(output_path)
            if output_format == 'json' or schema_file.suffix == '.json':
                with open(output_path, 'w') as f:
                    json.dump(schema, f, indent=2)
            elif output_format == 'yaml' or schema_file.suffix in ['.yaml', '.yml']:
                import yaml
                with open(output_path, 'w') as f:
                    yaml.dump(schema, f, default_flow_style=False)
            logger.info(f"Schema saved to {output_path}")

        return {
            "success": True,
            "schema": schema,
            "file": input_path
        }
    except Exception as e:
        logger.error(f"Infer schema failed: {e}")
        raise DatakitError(f"Schema inference failed: {e}") from e


# Map of all available agent functions for discovery
AGENT_FUNCTIONS = {
    "convert": {
        "function": convert,
        "schema": CONVERT_SCHEMA,
        "description": "Convert data between formats (CSV, JSON, YAML, TOML, XML, Parquet, Excel)"
    },
    "validate": {
        "function": validate,
        "schema": VALIDATE_SCHEMA,
        "description": "Validate data against a schema"
    },
    "filter": {
        "function": filter_data,
        "schema": FILTER_SCHEMA,
        "description": "Filter data by conditions"
    },
    "select": {
        "function": select,
        "schema": SELECT_SCHEMA,
        "description": "Select specific fields from data"
    },
    "merge": {
        "function": merge,
        "schema": MERGE_SCHEMA,
        "description": "Merge two datasets on a common field"
    },
    "summary": {
        "function": summary,
        "schema": SUMMARY_SCHEMA,
        "description": "Generate summary statistics for a dataset"
    },
    "sample": {
        "function": sample,
        "schema": SAMPLE_SCHEMA,
        "description": "Sample records from a dataset"
    },
    "infer_schema": {
        "function": infer_schema,
        "schema": INFER_SCHEMA_SCHEMA,
        "description": "Infer schema from data"
    }
}


def get_agent_function(name: str) -> Optional[Dict[str, Any]]:
    """Get agent function metadata by name."""
    return AGENT_FUNCTIONS.get(name)


def list_agent_functions() -> List[Dict[str, Any]]:
    """List all available agent functions with their schemas."""
    return [
        {
            "name": name,
            "description": info["description"],
            "schema": info["schema"]
        }
        for name, info in AGENT_FUNCTIONS.items()
    ]
