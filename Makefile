.PHONY: help install test lint format clean run docker-build docker-up docker-down

help: ## Show this help
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	pip install -r requirements.txt

test: ## Run tests
	pytest --cov=app --cov-report=html --cov-report=term

test-fast: ## Run tests without coverage
	pytest -x

lint: ## Run linters
	flake8 app tests
	mypy app

format: ## Format code
	black app tests
	isort app tests

clean: ## Clean cache and temporary files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .coverage htmlcov/ .pytest_cache/

run: ## Run application locally
	python run.py

docker-build: ## Build Docker image
	docker-compose build

docker-up: ## Start services with Docker Compose
	docker-compose up -d

docker-down: ## Stop services
	docker-compose down

docker-logs: ## Show Docker logs
	docker-compose logs -f

docker-shell: ## Shell into web container
	docker-compose exec web bash

docker-db: ## Connect to database
	docker-compose exec db psql -U twitter_user -d twitter_db

setup: ## Initial setup for development
	cp .env.example .env
	pip install -r requirements.txt
	@echo "Please edit .env file with your settings"

ci: lint test ## Run CI pipeline (lint + test)
