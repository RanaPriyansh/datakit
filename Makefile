.PHONY: help install dev-install test lint format type-check clean docker-build docker-run

help:
	@echo "datakit Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  install        Install package in editable mode"
	@echo "  dev-install    Install with development dependencies"
	@echo "  test           Run tests with pytest"
	@echo "  lint           Run linter (ruff)"
	@echo "  format         Auto-format code with black and isort"
	@echo "  type-check     Run mypy type checking"
	@echo "  all-checks     Run all quality checks (format, lint, type, test)"
	@echo "  clean          Remove build artifacts and cache"
	@echo "  docker-build   Build Docker image"
	@echo "  docker-run     Run Docker container interactively"

install:
	pip install -e .

dev-install:
	pip install -e ".[dev]"

test:
	pytest tests/ -v

test-cov:
	pytest tests/ --cov=datakit --cov-report=html --cov-report=term

lint:
	ruff src/ tests/

format:
	black src/ tests/
	isort src/ tests/

type-check:
	mypy src/ tests/

all-checks: format lint type-check test

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type d -name "dist" -exec rm -rf {} +
	find . -type d -name "build" -exec rm -rf {} +
	find . -name "*.egg-info" -exec rm -rf {} +
	rm -rf .coverage htmlcov/

docker-build:
	docker build -t datakit:latest .

docker-run:
	docker run -it --rm datakit:latest

# Example usage for agents
agent-example:
	@echo "Example agent usage:"
	@echo "  python -c \"from datakit.agent import convert; print(convert('input.csv', 'output.json'))\""
	@echo ""
	@echo "List agent functions:"
	@echo "  python -c \"from datakit.agent import list_agent_functions; print(list_agent_functions())\""
