.PHONY: help install install-dev sync test test-cov lint format format-check type-check clean run

help:
	@echo "Tandem Simulator - Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install      - Install dependencies using uv"
	@echo "  make install-dev  - Install with dev dependencies"
	@echo "  make sync         - Sync dependencies (alias for install-dev)"
	@echo ""
	@echo "Development:"
	@echo "  make run          - Run the simulator"
	@echo "  make test         - Run tests"
	@echo "  make test-cov     - Run tests with coverage"
	@echo "  make lint         - Run all linters"
	@echo "  make format       - Format code with black and isort"
	@echo "  make format-check - Check code formatting without changes"
	@echo "  make type-check   - Run type checking with mypy"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean        - Remove build artifacts and cache"

install:
	uv sync

install-dev:
	uv sync --all-extras

sync: install-dev

test:
	uv run pytest

test-cov:
	uv run pytest --cov=tandem_simulator --cov-report=term-missing --cov-report=html

lint:
	uv run flake8 tandem_simulator tests
	uv run pylint tandem_simulator --disable=all --enable=F,E

format:
	uv run black tandem_simulator simulator.py tests
	uv run isort tandem_simulator simulator.py tests

format-check:
	uv run black --check tandem_simulator simulator.py tests
	uv run isort --check-only tandem_simulator simulator.py tests

type-check:
	uv run mypy tandem_simulator

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

run:
	uv run python simulator.py

run-debug:
	uv run python simulator.py --debug

run-tui:
	uv run python simulator.py --tui
