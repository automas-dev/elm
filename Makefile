
setup:
	poetry install

lint:
	poetry run ruff format --check .
	poetry run ruff check .

format:
	poetry run ruff format .
	poetry run ruff check --fix .

test:
	poetry run pytest tests

.PHONY: setup lint format test
