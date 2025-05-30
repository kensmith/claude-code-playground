.PHONY: test lint format check
test: check
	uv run python -m pytest -s

lint:
	uv run ruff check src tests

format:
	uv run ruff format src tests

check: format
	uv run ruff check --fix src tests
