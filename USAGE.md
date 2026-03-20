# datakit Usage Guide

Comprehensive guide for using datakit both from CLI and as a Python library/agent.

## Quick Start

### Installation

```bash
# From PyPI (when published)
pip install datakit

# From source (development)
git clone https://github.com/RanaPriyansh/datakit.git
cd datakit
pip install -e ".[dev]"
```

### CLI Basics

```bash
# Convert CSV to JSON
datakit convert data.csv output.json

# Validate data
datakit validate data.json --schema schema.json

# Filter data (only records where age > 18)
datakit filter data.json --condition '{"age": {"gt": 18}}' -o filtered.json

# Get summary
datakit summary data.csv

# Sample random records
datakit sample data.json -n 10
```

## Agent Integration

datakit provides a clean Python API designed for AI agents and programmatic use.

### Basic Agent Usage

```python
from datakit.agent import convert, validate, summary

# Convert data
result = convert("input.csv", "output.json")
print(result)  # {'success': True, 'output_path': '...', ...}

# Validate with schema
validation = validate("data.json", schema={"name": "string", "age": "number"})
print(validation['valid'])  # True/False

# Get summary
result = summary("data.csv")
print(result['summary']['records'])  # Number of records
```

### Using with Hermes Agent

Add datakit as a skill in your Hermes Agent configuration. Example agent workflow:

```yaml
# In your agent's plan
steps:
  - tool: datakit.convert
    arguments:
      input_path: "raw_data.csv"
      output_path: "processed_data.json"
  - tool: datakit.validate
    arguments:
      input_path: "processed_data.json"
      schema:
        name: "string"
        age: "number"
        email: "string"
```

### Function Calling Schemas

Each agent function includes a JSON schema for LLM function calling:

```python
from datakit.agent import get_agent_function, AGENT_FUNCTIONS

# Get schema for a specific function
convert_info = get_agent_function("convert")
print(convert_info["schema"])
# {
#   "type": "object",
#   "properties": {
#     "input_path": {"type": "string", "description": "..."},
#     "output_path": {"type": "string", "description": "..."},
#     ...
#   },
#   "required": ["input_path", "output_path"]
# }

# List all available functions
for func in list_agent_functions():
    print(f"{func['name']}: {func['description']}")
```

### Structured Output for LLMs

All agent functions return structured dictionaries with `success` field and metadata:

```python
result = convert("a.csv", "b.json")
if result['success']:
    print(f"Output at: {result['output_path']}")
else:
    print(f"Error: {result.get('error')}")
```

## Environment Variables

Configure datakit behavior via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `DATATKIT_LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `DATATKIT_LOG_FILE` | (none) | Optional file path to write logs |
| `DATATKIT_LOG_JSON` | `false` | If set, use JSON log format |

Example:

```bash
export DATATKIT_LOG_LEVEL=DEBUG
export DATATKIT_LOG_FILE=/var/log/datakit.log
datakit convert input.csv output.json
```

## Error Handling

Agent functions raise specific exceptions:

- `DatakitError` - Base exception
- `ValidationError` - Schema validation failures
- `FileOperationError` - File read/write issues
- `FormatError` - Unsupported data format
- `SchemaError` - Schema-related errors

Example:

```python
from datakit.agent import convert
from datakit.exceptions import FileOperationError

try:
    result = convert("missing.csv", "out.json")
except FileOperationError as e:
    print(f"File error: {e}")
```

## Supported Formats

| Format | Extensions | Read | Write |
|--------|-----------|------|-------|
| CSV | .csv | ✓ | ✓ |
| JSON | .json | ✓ | ✓ |
| YAML | .yaml, .yml | ✓ | ✓ |
| TOML | .toml | ✓ | ✓ |
| XML | .xml | ✓ | ✓ |
| Parquet | .parquet | ✓ | ✓ |
| Excel | .xlsx, .xls | ✓ | ✓ |

## Advanced Usage

### Large Files with Streaming

For large files, use the `DataConverter` with pandas for efficient processing:

```python
from datakit.core import DataConverter

# Load with pandas (efficient for large CSV)
dataset = DataConverter.load("large.csv")
print(f"Loaded {len(dataset)} rows")
```

### Schema Inference

```python
from datakit.agent import infer_schema

schema = infer_schema("data.json")
print(schema)
# {'name': 'string', 'age': 'number', 'city': 'string'}
```

### Complex Filtering

```python
from datakit.agent import filter_data

conditions = {
    "age": {"gt": 18, "lt": 65},
    "status": "active",
    "score": {"gte": 75}
}
result = filter_data("users.json", conditions)
```

## Performance Tips

- For CSV/Excel files, pandas provides the best performance
- For small JSON/YAML, pure Python is fine
- Use `sample()` for quick previews of large datasets
- Convert to Parquet for compressed storage and fast column access

## Troubleshooting

**Issue**: `ModuleNotFoundError: No module named 'datakit'`
**Fix**: Ensure you've installed the package in your current environment:

```bash
pip install -e /path/to/datakit
# or add to PYTHONPATH
export PYTHONPATH=/path/to/datakit/src:$PYTHONPATH
```

**Issue**: Import errors for optional dependencies (openpyxl, pyarrow)
**Fix**: Install optional extras:

```bash
pip install "datakit[excel]"   # for Excel support
pip install "datakit[parquet]" # for Parquet support
pip install "datakit[all]"     # all formats
```

**Issue**: Memory errors on large files
**Fix**: Use chunked processing with pandas or increase available memory.

## CLI Reference

All CLI commands mirror agent functions:

| Agent Function | CLI Command |
|----------------|-------------|
| `convert()` | `datakit convert INPUT OUTPUT` |
| `validate()` | `datakit validate INPUT [--schema SCHEMA]` |
| `filter_data()` | `datakit filter INPUT --condition '{}' [--output OUT]` |
| `select()` | `datakit select INPUT --fields "f1,f2" [--output OUT]` |
| `merge()` | `datakit merge INPUT1 INPUT2 [--on FIELD] [--how TYPE]` |
| `summary()` | `datakit summary INPUT` |
| `sample()` | `datakit sample INPUT [-n N] [--method METHOD]` |
| `infer_schema()` | `datakit infer-schema INPUT [--output OUT]` |
