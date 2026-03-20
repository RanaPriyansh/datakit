# Merge Datasets Example

Merge two datasets on a common key.

## Datasets

**users.csv**

```csv
id,name,age
1,Alice,30
2,Bob,25
3,Charlie,35
```

**scores.csv**

```csv
id,score,department
1,85,Engineering
2,92,Marketing
3,78,Sales
```

## CLI

```bash
# Merge on 'id' field using outer join (keep all records)
datakit merge users.csv scores.csv --on id --how outer -o merged.json
```

## Agent API

```python
from datakit.agent import merge

result = merge(
    "users.csv",
    "scores.csv",
    on="id",
    how="outer"
)

# Full result if not saved to file
merged_data = result['data']
print(f"Merged {result['records']} records")

# Examine first record
print(merged_data[0])
# {'id': '1', 'name': 'Alice', 'age': '30', 'score': '85', 'department': 'Engineering'}
```

## Output (merged.json)

```json
[
  {"id": 1, "name": "Alice", "age": "30", "score": 85, "department": "Engineering"},
  {"id": 2, "name": "Bob", "age": "25", "score": 92, "department": "Marketing"},
  {"id": 3, "name": "Charlie", "age": "35", "score": 78, "department": "Sales"}
]
```

## Notes

- Ensure the join key (`--on`) exists in both datasets
- `how` options:
  - `inner`: only matching records from both
  - `left`: all from first + matching from second
  - `right`: all from second + matching from first
  - `outer`: all records from both (default)
- If `--on` is omitted, datasets are concatenated
