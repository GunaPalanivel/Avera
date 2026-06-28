.PHONY: help install lint test security validate validate-full ci download-model docker-build docker-run docker-sandbox

help:
	@echo "Targets: install lint test security validate validate-full ci download-model docker-build docker-run docker-sandbox"

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
	python rank.py --candidates tests/fixtures/sample.jsonl --limit 1 --out ci_submission.csv
	pytest tests/ -v

validate-full:
	python rank.py --candidates DataSet/candidates.jsonl --out submission.csv
	python DataSet/validate_submission.py submission.csv

ci: lint test security
	python rank.py --health
	python rank.py --candidates tests/fixtures/sample.jsonl --limit 1 --out ci_submission.csv
	python -c "import csv; from pathlib import Path; rows=list(csv.reader(Path('ci_submission.csv').open(encoding='utf-8'))); assert rows[0]==['candidate_id','rank','score','reasoning']; assert len(rows)>=2"

download-model:
	python scripts/download_model.py

docker-build:
	docker-compose build

docker-run:
	docker-compose run --rm avera-cli

docker-sandbox:
	docker-compose up avera-sandbox
