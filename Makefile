.PHONY: help install lint test security validate

help:
	@echo "Targets: install lint test security validate"

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
