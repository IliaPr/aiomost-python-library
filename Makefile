.PHONY: help install install-dev test lint format clean build upload

help:
	@echo "Available commands:"
	@echo "  install     - Install the package"
	@echo "  install-dev - Install package in development mode with dev dependencies"
	@echo "  test        - Run tests"
	@echo "  lint        - Run linting (flake8, mypy)"
	@echo "  format      - Format code (black, isort)"
	@echo "  clean       - Clean build artifacts"
	@echo "  build       - Build package"
	@echo "  upload      - Upload to PyPI"

install:
	pip install .

install-dev:
	pip install -e ".[dev]"

test:
	pytest

lint:
	flake8 src tests
	mypy src

format:
	black src tests
	isort src tests

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	python -m build

upload: build
	python -m twine upload dist/*

dev-setup:
	pip install build twine
	pip install -e ".[dev]"
