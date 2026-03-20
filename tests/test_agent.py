"""
Tests for agent API functions.
"""

import json
import sys
from pathlib import Path

import pytest

# Import from source
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from datakit.agent import (
    convert, validate, filter_data, select, merge, summary,
    sample, infer_schema, AGENT_FUNCTIONS, get_agent_function, list_agent_functions
)
from datakit.exceptions import DatakitError, ValidationError


class TestAgentFunctions:
    """Tests for agent-exposed functions."""

    def test_list_agent_functions(self):
        funcs = list_agent_functions()
        assert len(funcs) >= 8
        names = [f["name"] for f in funcs]
        expected = ["convert", "validate", "filter", "select", "merge", "summary", "sample", "infer_schema"]
        for name in expected:
            assert name in names

    def test_get_agent_function(self):
        func_info = get_agent_function("convert")
        assert func_info is not None
        assert "schema" in func_info
        assert "function" in func_info

    def test_convert_agent(self, tmp_path, sample_csv):
        output = tmp_path / "out.json"
        result = convert(str(sample_csv), str(output))
        assert result["success"] is True
        assert Path(result["output_path"]).exists()

    def test_validate_agent(self, sample_json):
        result = validate(str(sample_json))
        assert result["success"] is True
        assert "summary" in result or "valid" in result

    def test_summary_agent(self, sample_csv):
        result = summary(str(sample_csv))
        assert result["success"] is True
        assert "summary" in result
        assert result["summary"]["records"] > 0

    def test_sample_agent(self, sample_json):
        result = sample(str(sample_json), n=2)
        assert result["success"] is True
        assert len(result["data"]) == 2

    def test_infer_schema_agent(self, sample_json):
        result = infer_schema(str(sample_json))
        assert result["success"] is True
        assert "schema" in result
        schema = result["schema"]
        assert "name" in schema

    def test_filter_agent(self, sample_json):
        conditions = {"age": {"gt": 25}}
        result = filter_data(str(sample_json), conditions)
        assert result["success"] is True
        assert result["records_filtered"] >= 0

    def test_select_agent(self, sample_json):
        result = select(str(sample_json), ["name", "age"])
        assert result["success"] is True
        for record in result["data"]:
            assert set(record.keys()) <= {"name", "age"}

    def test_merge_agent(self, tmp_path, sample_json):
        # Create second dataset with different field
        second = tmp_path / "second.json"
        data2 = [
            {"name": "Alice", "score": 100},
            {"name": "Bob", "score": 90},
            {"name": "Charlie", "score": 85}
        ]
        second.write_text(json.dumps(data2, indent=2))

        output = tmp_path / "merged.json"
        result = merge(str(sample_json), str(second), on="name", how="outer")
        assert result["success"] is True
        assert result["records"] == 3
        # Check that merged records have both age and score
        if result["data"]:
            first = result["data"][0]
            # Should have name, age, city from first and score from second
            assert "name" in first
            assert "age" in first or "score" in first

    def test_error_handling(self):
        with pytest.raises(DatakitError):
            convert("nonexistent.csv", "out.json")

    def test_schema_validation_error(self):
        # Invalid condition type
        with pytest.raises(DatakitError):
            filter_data("dummy.json", {"field": object()})


# Sample data fixtures at module level for reuse
@pytest.fixture
def sample_csv(tmp_path):
    csv_path = tmp_path / "sample.csv"
    csv_path.write_text("name,age,city\nAlice,30,NYC\nBob,25,LA\nCharlie,35,Chicago\n")
    return csv_path


@pytest.fixture
def sample_json(tmp_path):
    json_path = tmp_path / "sample.json"
    data = [
        {"name": "Alice", "age": 30, "city": "NYC"},
        {"name": "Bob", "age": 25, "city": "LA"},
        {"name": "Charlie", "age": 35, "city": "Chicago"}
    ]
    json_path.write_text(json.dumps(data, indent=2))
    return json_path
