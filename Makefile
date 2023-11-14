.PHONY: default
check: lint format types

.PHONY: lint
lint:
	flake8 . --exclude .venv --count --show-source --statistics \
		--select=E9,F63,F7,F82

.PHONY: format
format:
	ruff format --check .

.PHONY: types
types:
	mypy .
