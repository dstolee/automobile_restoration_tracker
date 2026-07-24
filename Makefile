.PHONY: install dev test coverage lint format audit run docker-up docker-down

install:
	python -m pip install -e .

dev:
	python -m pip install -e ".[dev]"

test:
	pytest

coverage:
	pytest --cov=app --cov-report=term-missing --cov-report=html

lint:
	ruff check .
	ruff format --check .

format:
	ruff check --fix .
	ruff format .

audit:
	pip-audit

run:
	flask --app run.py --debug run --host 0.0.0.0

docker-up:
	docker compose up -d --build

docker-down:
	docker compose down
