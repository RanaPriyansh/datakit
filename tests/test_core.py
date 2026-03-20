"""
Tests for datakit core functionality.
"""

import json
import os
import tempfile
from pathlib import Path

import pytest

# Import directly from source since package may not be installed
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from datakit.core import DataConverter, DataValidator, DataFilter, DataMerger, DataSampler, Dataset
from datakit.exceptions import ValidationError


class TestDataConverter:
    """Tests for DataConverter class."""

    def test_detect_format(self):
        assert DataConverter.detect_format("file.csv") == "csv"
        assert DataConverter.detect_format("file.json") == "json"
        assert DataConverter.detect_format("file.yaml") == "yaml"
        assert DataConverter.detect_format("file.yml") == "yaml"
        assert DataConverter.detect_format("file.toml") == "toml"
        assert DataConverter.detect_format("file.xml") == "xml"
        assert DataConverter.detect_format("file.parquet") == "parquet"
        assert DataConverter.detect_format("file.xlsx") == "excel"
        assert DataConverter.detect_format("file.xls") == "excel"
        assert DataConverter.detect_format("file.unknown") == "unknown"

    def test_load_csv(self, sample_csv):
        dataset = DataConverter.load(sample_csv)
        assert isinstance(dataset.data, list)
        assert len(dataset.data) == 3
        assert dataset.format == "csv"
        assert "name" in dataset.as_dicts[0]

    def test_load_json(self, sample_json):
        dataset = DataConverter.load(sample_json)
        assert len(dataset.data) == 3
        assert dataset.format == "json"

    def test_load_yaml(self, sample_yaml):
        dataset = DataConverter.load(sample_yaml)
        assert len(dataset.data) == 3
        assert dataset.format == "yaml"

    def test_load_toml(self, sample_toml):
        dataset = DataConverter.load(sample_toml)
        assert len(dataset.data) == 3
        assert dataset.format == "toml"

    def test_save_json(self, temp_dir, sample_csv):
        input_path = sample_csv
        output_path = temp_dir / "output.json"
        result = DataConverter.convert(str(input_path), str(output_path))
        assert Path(result).exists()
        with open(result) as f:
            data = json.load(f)
        assert len(data) == 3

    def test_save_csv(self, temp_dir, sample_json):
        input_path = sample_json
        output_path = temp_dir / "output.csv"
        result = DataConverter.convert(str(input_path), str(output_path))
        assert Path(result).exists()
        content = Path(result).read_text()
        assert "name,age,city" in content

    def test_convert_missing_file(self):
        with pytest.raises(FileNotFoundError):
            DataConverter.load("nonexistent.csv")

    def test_as_dataframe(self, sample_json):
        dataset = DataConverter.load(sample_json)
        df = dataset.as_dataframe
        assert len(df) == 3
        assert list(df.columns) == ["name", "age", "city"]

    def test_as_dicts(self, sample_csv):
        dataset = DataConverter.load(sample_csv)
        dicts = dataset.as_dicts
        assert isinstance(dicts, list)
        assert isinstance(dicts[0], dict)


class TestDataValidator:
    """Tests for DataValidator class."""

    def test_validate_schema_valid(self):
        data = [
            {"name": "Alice", "age": 30, "active": True},
            {"name": "Bob", "age": 25, "active": False}
        ]
        schema = {"name": "string", "age": "number", "active": "boolean"}
        result = DataValidator.validate_schema(data, schema)
        assert result["valid"] is True
        assert len(result["errors"]) == 0

    def test_validate_schema_missing_field(self):
        data = [{"name": "Alice", "age": 30}]
        schema = {"name": "string", "age": "number", "active": "boolean"}
        result = DataValidator.validate_schema(data, schema)
        assert result["valid"] is False
        assert any("Missing field" in err for err in result["errors"])

    def test_validate_schema_type_mismatch(self):
        data = [{"name": "Alice", "age": "thirty", "active": True}]
        schema = {"name": "string", "age": "number", "active": "boolean"}
        result = DataValidator.validate_schema(data, schema)
        assert result["valid"] is False
        assert any("Expected number" in err for err in result["errors"])

    def test_validate_empty_data(self):
        result = DataValidator.validate_schema([], {"field": "string"})
        assert result["valid"] is True
        assert "No data to validate" in result["warnings"]

    def test_infer_schema(self):
        data = [
            {"name": "Alice", "age": 30, "active": True, "score": 95.5},
            {"name": "Bob", "age": 25, "active": False, "score": 87.0}
        ]
        schema = DataValidator.infer_schema(data)
        assert schema["name"] == "string"
        assert schema["age"] == "number"
        assert schema["active"] == "boolean"
        assert schema["score"] == "number"


class TestDataFilter:
    """Tests for DataFilter class."""

    def test_filter_eq(self):
        data = [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25},
            {"name": "Charlie", "age": 30}
        ]
        conditions = {"age": 30}
        result = DataFilter.filter(data, conditions)
        assert len(result) == 2
        assert all(r["age"] == 30 for r in result)

    def test_filter_nested_conditions(self):
        data = [
            {"name": "Alice", "age": 30, "score": 85},
            {"name": "Bob", "age": 25, "score": 90},
            {"name": "Charlie", "age": 35, "score": 80}
        ]
        conditions = {"age": {"gt": 25}, "score": {"gt": 80}}
        result = DataFilter.filter(data, conditions)
        assert len(result) == 2  # Alice (30>25,85>80) and Charlie (35>25,80 not >80? Actually 80>80 is False, so only Alice? Wait)
        # Actually Charlie has score 80, condition "gt": 80 means 80>80 is false. So only Alice qualifies.
        # Let's correct: Alice age 30 > 25 and score 85 > 80 -> pass
        # Bob age 25 not > 25 -> fail
        # Charlie age 35 > 25 but score 80 > 80 false -> fail
        assert len(result) == 1
        assert result[0]["name"] == "Alice"

    def test_filter_in_condition(self):
        data = [
            {"name": "Alice", "city": "NYC"},
            {"name": "Bob", "city": "LA"},
            {"name": "Charlie", "city": "Chicago"}
        ]
        conditions = {"city": {"in": ["NYC", "LA"]}}
        result = DataFilter.filter(data, conditions)
        assert len(result) == 2

    def test_select(self):
        data = [
            {"name": "Alice", "age": 30, "city": "NYC"},
            {"name": "Bob", "age": 25, "city": "LA"}
        ]
        result = DataFilter.select(data, ["name", "age"])
        assert len(result) == 2
        assert set(result[0].keys()) == {"name", "age"}

    def test_transform(self):
        data = [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25}
        ]
        transformations = {"age": {"add": 1}}
        result = DataFilter.transform(data, transformations)
        assert result[0]["age"] == 31
        assert result[1]["age"] == 26

    def test_transform_uppercase(self):
        data = [{"name": "alice"}, {"name": "bob"}]
        transformations = {"name": "uppercase"}
        result = DataFilter.transform(data, transformations)
        assert result[0]["name"] == "ALICE"


class TestDataMerger:
    """Tests for DataMerger class."""

    def test_merge_concat(self):
        data1 = [{"id": 1, "name": "Alice"}]
        data2 = [{"id": 2, "name": "Bob"}]
        result = DataMerger.merge(data1, data2, on=None, how="outer")
        assert len(result) == 2

    def test_merge_inner(self):
        data1 = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
        data2 = [{"id": 1, "value": 100}, {"id": 3, "value": 300}]
        result = DataMerger.merge(data1, data2, on="id", how="inner")
        assert len(result) == 1
        assert result[0]["id"] == 1
        assert result[0]["name"] == "Alice"
        assert result[0]["value"] == 100

    def test_merge_left(self):
        data1 = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
        data2 = [{"id": 1, "value": 100}]
        result = DataMerger.merge(data1, data2, on="id", how="left")
        assert len(result) == 2
        assert result[0].get("value") == 100
        assert result[1].get("value") is None

    def test_merge_right(self):
        data1 = [{"id": 1, "name": "Alice"}]
        data2 = [{"id": 1, "value": 100}, {"id": 2, "value": 200}]
        result = DataMerger.merge(data1, data2, on="id", how="right")
        assert len(result) == 2

    def test_merge_outer(self):
        data1 = [{"id": 1, "name": "Alice"}]
        data2 = [{"id": 2, "value": 200}]
        result = DataMerger.merge(data1, data2, on="id", how="outer")
        assert len(result) == 2

    def test_concat(self):
        data1 = [{"id": 1}, {"id": 2}]
        data2 = [{"id": 3}]
        result = DataMerger.concat([data1, data2])
        assert len(result) == 3


class TestDataSampler:
    """Tests for DataSampler class."""

    def test_sample_random(self):
        data = [{"id": i} for i in range(100)]
        result = DataSampler.sample(data, n=10, method="random")
        assert len(result) == 10
        # Ensure unique samples
        ids = [r["id"] for r in result]
        assert len(set(ids)) == 10

    def test_sample_first(self):
        data = [{"id": i} for i in range(10)]
        result = DataSampler.sample(data, n=3, method="first")
        assert result[0]["id"] == 0
        assert result[1]["id"] == 1
        assert result[2]["id"] == 2

    def test_sample_last(self):
        data = [{"id": i} for i in range(10)]
        result = DataSampler.sample(data, n=3, method="last")
        assert result[0]["id"] == 7
        assert result[1]["id"] == 8
        assert result[2]["id"] == 9

    def test_sample_n_larger_than_data(self):
        data = [{"id": 1}, {"id": 2}]
        result = DataSampler.sample(data, n=5, method="first")
        assert len(result) == 2

    def test_summary(self, sample_json):
        # Load data first
        dataset = DataConverter.load(sample_json)
        summary = DataSampler.summary(dataset.as_dicts)
        assert summary["records"] == 3
        assert "name" in summary["fields"]
        assert "age" in summary["fields"]
        assert "city" in summary["fields"]
