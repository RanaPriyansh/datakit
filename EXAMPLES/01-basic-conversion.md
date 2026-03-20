# Basic Conversion Example

Convert a CSV file to JSON with datakit.

## Input (data.csv)

```csv
name,age,city
Alice,30,NYC
Bob,25,LA
Charlie,35,Chicago
```

## CLI

```bash
datakit convert data.csv output.json
```

## Output (output.json)

```json
[
  {"name": "Alice", "age": "30", "city": "NYC"},
  {"name": "Bob", "age": "25", "city": "LA"},
  {"name": "Charlie", "age": "35", "city": "Chicago"}
]
```

## Agent API

```python
from datakit.agent import convert

result = convert("data.csv", "output.json")
print(f"Success: {result['success']}")
print(f"Output file: {result['output_path']}")
```
