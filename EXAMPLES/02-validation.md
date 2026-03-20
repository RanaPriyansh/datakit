# Validation Example

Validate data against a schema using datakit.

## Schema (user_schema.json)

```json
{
  "name": "string",
  "age": "number",
  "email": "string"
}
```

## Input (users.json)

```json
[
  {"name": "Alice", "age": 30, "email": "alice@example.com"},
  {"name": "Bob", "age": 25, "email": "bob@example.com"},
  {"name": "Charlie", "age": "thirty-five", "email": "charlie@example.com"}
]
```

## CLI

```bash
datakit validate users.json --schema user_schema.json --json
```

## Agent API

```python
from datakit.agent import validate

schema = {
    "name": "string",
    "age": "number",
    "email": "string"
}

result = validate("users.json", schema=schema)
print(f"Valid: {result['valid']}")
print(f"Errors: {len(result['errors'])}")
for err in result['errors'][:5]:
    print(f"  - {err}")
```

## Output

```json
{
  "success": true,
  "valid": false,
  "errors": [
    "Record 2: field 'age': Expected number, got str"
  ],
  "warnings": [],
  "records_checked": 3
}
```
