# datakit Architecture

Design principles, internal structure, and extension points.

## Design Philosophy

datakit follows these principles:

1. **Simplicity**: One tool, one job. Each function does one thing well.
2. **Composability**: Functions can be chained together for complex workflows.
3. **Agent-First**: API designed for AI agents with structured I/O and clear schemas.
4. **Format Agnostic**: Support many formats with consistent interface.
5. **Type Safety**: Full type hints and mypy compliance.
6. **Production Ready**: Comprehensive tests, logging, error handling.

## Architecture Overview

```
datakit/
├── cli.py              # Command-line interface (argparse)
├── core.py             # Core conversion/validation logic
├── agent.py            # Agent-friendly API wrappers with schemas
├── exceptions.py       # Custom exception hierarchy
├── logging_config.py   # Structured logging setup
└── __init__.py         # Public API exports
```

### Core Layer (`core.py`)

- `Dataset` - Dataclass holding data + metadata
- `DataConverter` - Static methods for format conversion
- `DataValidator` - Schema validation and inference
- `DataFilter` - Filtering, selection, transformation
- `DataMerger` - Dataset joining and concatenation
- `DataSampler` - Sampling and summary statistics

**Key insight**: The core layer is pure Python with minimal dependencies. Format-specific code is isolated.

### CLI Layer (`cli.py`)

- Uses `argparse` for subcommand parsing
- Each subcommand calls corresponding agent function
- Handles errors and exit codes properly
- Provides helpful examples in epilog

### Agent Layer (`agent.py`)

- Thin wrappers around core functions
- Returns structured dictionaries (no exceptions)
- Includes JSON schemas for function calling
- Limits output size (truncation) for agent consumption
- Comprehensive logging

### Error Handling

All operations can raise:
- `DatakitError` - base exception
- `FileOperationError` - I/O failures
- `ValidationError` - schema validation failures
- `FormatError` - unsupported format
- `SchemaError` - schema issues

The CLI catches these and prints user-friendly messages. Agent functions let exceptions propagate for programmatic handling.

### Logging

- Uses Python's standard `logging` module
- Configured via `setup_logging()`
- Respects `DATATKIT_LOG_LEVEL` env var
- Optional JSON format for structured logs
- File logging supported

## Data Flow

### Conversion

```
Input File
    ↓
DataConverter.load(path)
    → Detects format (extension or explicit)
    → Parses into Dataset.data (list[dict] or DataFrame)
    → Dataset.format = detected
    ↓
Operation (filter/merge/etc)
    ↓
DataConverter.save(dataset, output_path)
    → Detects output format
    → Serializes to appropriate format
    → Creates parent directories if needed
```

### Validation

```
Data + Schema
    ↓
DataValidator.validate_schema(data, schema)
    → Checks all required fields present
    → Type checks each value
    → Collects errors/warnings
    ↓
Result: {'valid': bool, 'errors': [], 'warnings': []}
```

## Extension Points

### Adding a New Format

1. Add detection in `DataConverter.detect_format()`:
   ```python
   format_map = {..., '.new': 'new'}
   ```

2. Add loading logic in `DataConverter.load()`:
   ```python
   elif format == 'new':
       with open(path) as f:
           data = parse_new_format(f)
   ```

3. Add saving logic in `DataConverter.save()`:
   ```python
   elif format == 'new':
       with open(path, 'w') as f:
           f.write(serialize_new_format(dataset.data))
   ```

4. Add optional dependencies in `pyproject.toml`:
   ```toml
   [project.optional-dependencies]
   new = ["new-format-library>=1.0"]
   ```

### Adding a New Agent Function

1. Implement core logic in `core.py` or a new module.
2. Create wrapper in `agent.py`:
   - Function with clear parameters and return dict
   - Add to `AGENT_FUNCTIONS` dict
   - Define JSON schema
   - Add to `list_agent_functions()`
3. Add CLI subcommand in `cli.py`
4. Add tests in `tests/test_agent.py` and `tests/test_cli.py`
5. Update documentation

### Adding a New Filter/Transform Operation

Add a method to `DataFilter`:

```python
@staticmethod
def my_operation(data: List[Dict], params...) -> List[Dict]:
    # implementation
    return result
```

Then expose via agent and CLI.

## Performance Considerations

- **CSV**: Uses built-in `csv.DictReader` for streaming (memory efficient)
- **JSON**: Loads entire file into memory (use streaming for huge files)
- **YAML**: Uses `yaml.safe_load` (consider `yaml.safe_load_all` for multi-doc)
- **Parquet/Excel**: Uses pandas (fast but memory heavy)
- **Large files**: Consider chunking with pandas `read_csv(chunksize=)`

## Testing Strategy

- **Unit tests**: Core classes in `test_core.py`
- **Integration tests**: End-to-end CLI in `test_cli.py`
- **Agent tests**: API functions in `test_agent.py`
- **Fixtures**: Reusable sample data in `conftest.py`
- **Coverage target**: >90%

Run with:

```bash
pytest tests/ -v --cov=datakit
```

## Type Hints

- All functions have complete type hints
- `py.typed` file indicates type information available
- Mypy strict mode (except pandas)
- Compatible with IDEs and type checkers

## Future Roadmap

- [ ] Add database import/export (PostgreSQL, SQLite, MySQL)
- [ ] Add schema registry (JSON Schema, OpenAPI)
- [ ] Add diff/patches between datasets
- [ ] Add data cleaning utilities (deduplication, normalization)
- [ ] Add streaming API for huge files
- [ ] Add REST API server mode (FastAPI)
- [ ] Add plugin system for custom formats
- [ ] Integration with more Hermes skills (e.g., direct database connections)

## Contributing

See `CONTRIBUTING.md` for development workflow.

Key points:
- Fork and create feature branch
- Follow existing patterns
- Add tests for new features
- Run `make all-checks` before PR
- Ensure CI passes
