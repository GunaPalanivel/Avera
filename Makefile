.PHONY: help install lint test security validate docker-build docker-run docker-sandbox

help:
	@echo "Targets: install lint test security validate docker-build docker-run docker-sandbox"

install:
	pip install -r requirements.txt

lint:
	ruff check .
	ruff format --check .

test:
	pytest tests/ -v

security:
	bandit -r src/ -ll
	pip-audit -r requirements.txt

validate:
	python rank.py --health
	python rank.py --candidates tests/fixtures/sample.jsonl --limit 3
	pytest tests/ -v

docker-build:
	docker-compose build

docker-run:
	docker-compose run --rm avera-cli

docker-sandbox:
	docker-compose up avera-sandbox
