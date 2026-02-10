.PHONY: help install dev build up down logs restart clean test

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install dependencies using uv (syncs dependencies from pyproject.toml)
	uv sync

dev: ## Run in development mode (local)
	uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000

run: ## Run the application
	uv run python main.py

build: ## Build Docker images
	docker-compose build

up: ## Start all services with Docker Compose
	docker-compose up -d

down: ## Stop all services
	docker-compose down

logs: ## View logs from all services
	docker-compose logs -f

logs-api: ## View logs from API service only
	docker-compose logs -f api

logs-rabbitmq: ## View logs from RabbitMQ service only
	docker-compose logs -f rabbitmq

restart: ## Restart all services
	docker-compose restart

restart-api: ## Restart API service only
	docker-compose restart api

clean: ## Stop and remove all containers, networks, and volumes
	docker-compose down -v
	rm -rf data/*

test-map: ## Send a test map processing request
	uv run python test_example.py map

test-tsp: ## Send a test TSP request
	uv run python test_example.py tsp

test-consume: ## Consume responses from queues
	uv run python test_example.py consume

test-full: ## Run full test (map + tsp + consume)
	uv run python test_example.py full

test-algorithms: ## Test and compare TSP algorithms
	uv run python test_tsp_algorithms.py

ps: ## Show running containers
	docker-compose ps

shell-api: ## Open shell in API container
	docker-compose exec api /bin/sh

shell-rabbitmq: ## Open shell in RabbitMQ container
	docker-compose exec rabbitmq /bin/sh
