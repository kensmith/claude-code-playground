.PHONY: test lint format check
test: check
	poetry run python -m pytest -s

lint:
	poetry run ruff check src tests

format:
	poetry run ruff format src tests

check: format
	poetry run ruff check --fix src tests
