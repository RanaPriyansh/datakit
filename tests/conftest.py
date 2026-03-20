"""
Pytest configuration and fixtures for datakit tests.
"""

import json
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_csv(temp_dir):
    """Create a sample CSV file."""
    csv_path = temp_dir / "sample.csv"
    csv_path.write_text("name,age,city\nAlice,30,NYC\nBob,25,LA\nCharlie,35,Chicago\n")
    return csv_path


@pytest.fixture
def sample_json(temp_dir):
    """Create a sample JSON file."""
    json_path = temp_dir / "sample.json"
    data = [
        {"name": "Alice", "age": 30, "city": "NYC"},
        {"name": "Bob", "age": 25, "city": "LA"},
        {"name": "Charlie", "age": 35, "city": "Chicago"}
    ]
    json_path.write_text(json.dumps(data, indent=2))
    return json_path


@pytest.fixture
def sample_yaml(temp_dir):
    """Create a sample YAML file."""
    yaml_path = temp_dir / "sample.yaml"
    yaml_content = """
- name: Alice
  age: 30
  city: NYC
- name: Bob
  age: 25
  city: LA
- name: Charlie
  age: 35
  city: Chicago
"""
    yaml_path.write_text(yaml_content)
    return yaml_path


@pytest.fixture
def sample_toml(temp_dir):
    """Create a sample TOML file."""
    toml_path = temp_dir / "sample.toml"
    toml_content = """
[[record]]
name = "Alice"
age = 30
city = "NYC"

[[record]]
name = "Bob"
age = 25
city = "LA"

[[record]]
name = "Charlie"
age = 35
city = "Chicago"
"""
    toml_path.write_text(toml_content)
    return toml_path
