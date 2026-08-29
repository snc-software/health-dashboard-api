.DEFAULT_GOAL := help
VENV := ../.venv
PY := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

.PHONY: help venv install lock run dev test test-cov lint format typecheck check migrate migrate-down docker-build clean

help: ## Show this help
	@grep -hE '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

venv: ## Create the virtual environment
	python3 -m venv $(VENV)

install: venv ## Install the project with dev dependencies
	$(PIP) install --upgrade pip
	$(PIP) install -e ".[dev]"

lock: ## Regenerate the lock files (run after changing dependencies)
	./scripts/lock.sh

run: ## Run the API (production-style)
	$(VENV)/bin/fastapi run template_service/main.py

dev: ## Run the API with reload
	$(VENV)/bin/fastapi dev template_service/main.py

test: ## Run the test suite
	$(PY) -m pytest -v

test-cov: ## Run the test suite with coverage
	$(PY) -m pytest --cov --cov-report=term-missing

lint: ## Lint
	$(VENV)/bin/ruff check .

format: ## Auto-format and fix what can be fixed
	$(VENV)/bin/ruff format .
	$(VENV)/bin/ruff check --fix .

typecheck: ## Type-check
	$(VENV)/bin/mypy

check: lint typecheck test ## Everything CI runs

migrate: ## Apply database migrations
	cd migrations && goose up

migrate-down: ## Roll back the last migration
	cd migrations && goose down

docker-build: ## Build the container image
	docker build -t template-service:local .

clean: ## Remove caches and build artefacts
	rm -rf .pytest_cache .ruff_cache .mypy_cache .coverage coverage.xml htmlcov build dist *.egg-info
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
