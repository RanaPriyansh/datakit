# 📊 datakit – Data Format Converter Toolkit

**The complete toolkit for data format conversion and manipulation.**

Convert, validate, filter, merge, and transform data between CSV, JSON, YAML, TOML, XML, Parquet, and Excel.

## Quick Start

```bash
# 1️⃣ Install
pip install datakit

# 2️⃣ Convert CSV to JSON
datakit convert data.csv data.json

# 3️⃣ Validate data against schema
datakit validate data.json --schema schema.json

# 4️⃣ Filter data
datakit filter data.json --condition '{"age": {"gt": 18}}'

# 5️⃣ Merge datasets
datakit merge users.csv orders.json --on user_id --how left

# 6️⃣ Get summary statistics
datakit summary data.csv
```

## Supported Formats

| Format | Read | Write | Notes |
|--------|------|-------|-------|
| CSV | ✅ | ✅ | Standard comma-separated values |
| JSON | ✅ | ✅ | Arrays and objects |
| YAML | ✅ | ✅ | Human-readable data serialization |
| TOML | ✅ | ✅ | Configuration files |
| XML | ✅ | ✅ | Hierarchical data |
| Parquet | ✅ | ✅ | Columnar storage (requires pyarrow) |
| Excel | ✅ | ✅ | .xlsx files (requires openpyxl) |
| SQLite | ✅ | ❌ | Via pandas |

## Commands Reference

| Command | Description |
|---------|-------------|
| `convert` | Convert between data formats |
| `validate` | Validate data against schema |
| `filter` | Filter data by conditions |
| `select` | Select specific fields |
| `merge` | Merge datasets |
| `summary` | Generate summary statistics |
| `sample` | Sample data (random, first, last) |
| `infer-schema` | Infer schema from data |

## Examples

### Convert CSV to JSON with pretty printing
```bash
datakit convert customers.csv customers.json
# Creates nicely formatted JSON
```

### Validate API response data
```bash
datakit validate api_response.json --schema api_schema.json
# Checks all required fields are present
```

### Filter users by age and country
```bash
datakit filter users.json \
  --condition '{"age": {"gt": 18}, "country": {"eq": "US"}}' \
  -o adult_us_users.json
```

### Merge customer and order data
```bash
datakit merge customers.csv orders.csv \
  --on customer_id --how left \
  -o customer_orders.csv
```

### Sample random records for testing
```bash
datakit sample large_dataset.csv -n 100 --method random \
  -o test_sample.csv
```

### Get data summary
```bash
datakit summary sales_data.csv
# Shows record count, field types, missing values, statistics
```

## Python API

```python
from datakit import DataConverter, DataValidator, DataFilter

# Convert CSV to JSON
dataset = DataConverter.load("data.csv")
DataConverter.save(dataset, "data.json")

# Validate against schema
schema = {"name": "string", "age": "number", "active": "boolean"}
result = DataValidator.validate_schema(dataset.as_dicts, schema)
if result['valid']:
    print(f"Valid! {result['records_checked']} records")

# Filter data
filtered = DataFilter.filter(dataset.as_dicts, {"age": {"gt": 21}})
```

## Use Cases

### For Data Engineers
- Convert between data formats in ETL pipelines
- Validate data quality before loading into databases
- Sample large datasets for testing
- Generate summary statistics for data profiling

### For API Developers
- Convert API responses between formats
- Validate request/response schemas
- Filter and transform data for different clients
- Merge data from multiple API endpoints

### For Data Scientists
- Convert datasets to preferred formats (Parquet for speed)
- Sample data for exploratory analysis
- Merge datasets from different sources
- Generate summary statistics for data understanding

### For DevOps/Infrastructure
- Convert configuration files between formats
- Validate infrastructure-as-code templates
- Merge configuration fragments
- Transform log data for analysis

## Data Operations

### Filtering Conditions
```python
# Equal to
{"status": {"eq": "active"}}

# Not equal to
{"role": {"ne": "admin"}}

# Greater than
{"price": {"gt": 100}}

# Less than
{"quantity": {"lt": 10}}

# In list
{"category": {"in": ["electronics", "books"]}}
```

### Merge Types
- **inner**: Keep only matching records
- **left**: Keep all from first dataset
- **right**: Keep all from second dataset  
- **outer**: Keep all records from both

### Transformations
```python
# Convert to uppercase
{"name": "uppercase"}

# Convert to lowercase
{"email": "lowercase"}

# Strip whitespace
{"description": "strip"}

# Add value
{"price": {"add": 10}}

# Multiply value
{"quantity": {"multiply": 2}}
```

## Installation

### Basic (CSV, JSON, YAML, TOML, XML)
```bash
pip install datakit
```

### With Excel support
```bash
pip install datakit[excel]
```

### With Parquet support
```bash
pip install datakit[parquet]
```

### Everything
```bash
pip install datakit[all]
```

## System Requirements

- Python 3.8+
- No system dependencies for basic usage
- Optional: openpyxl (for Excel), pyarrow (for Parquet)

## License

MIT – Use it for anything.

---

*Built with ❤️ for data professionals. Never wrestle with data formats again.*
