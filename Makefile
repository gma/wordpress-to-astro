.PHONY: default
check: lint format types

.PHONY: lint
lint:
	ruff check . --select E9,F63,F7,F82 --show-source

.PHONY: format
format:
	ruff format --check .

.PHONY: types
types:
	mypy .
