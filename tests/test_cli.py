"""
Tests for datakit CLI.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest


def run_cli(args: list[str]) -> subprocess.CompletedProcess:
    """Run datakit CLI command and return result."""
    # Use the installed CLI if available, otherwise run via python -m
    cmd = ["datakit"] + args
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
    except FileNotFoundError:
        # Fallback to python module execution
        cmd = [sys.executable, "-m", "datakit.cli"] + args
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=Path(__file__).parent.parent
        )
    return result


class TestCLI:
    """CLI integration tests."""

    def test_help(self):
        result = run_cli(["--help"])
        assert result.returncode == 0
        assert "datakit" in result.stdout.lower()
        assert "convert" in result.stdout

    def test_version(self):
        result = run_cli(["--version"])
        assert result.returncode == 0
        assert "1.0.0" in result.stdout or "datakit" in result.stdout.lower()

    def test_convert_csv_to_json(self, tmp_path, sample_csv):
        output = tmp_path / "output.json"
        result = run_cli(["convert", str(sample_csv), str(output)])
        assert result.returncode == 0
        assert output.exists()
        data = json.loads(output.read_text())
        assert len(data) == 3

    def test_validate_json(self, tmp_path, sample_json):
        output = tmp_path / "validation.json"
        result = run_cli(["validate", str(sample_json), "--json"])
        assert result.returncode == 0
        validation = json.loads(result.stdout)
        assert "valid" in validation

    def test_summary(self, sample_csv):
        result = run_cli(["summary", str(sample_csv)])
        assert result.returncode == 0
        assert "Records:" in result.stdout or "Dataset Summary" in result.stdout

    # Note: Other CLI tests (filter, select, merge, sample, infer-schema) omitted for brevity
