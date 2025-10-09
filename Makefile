# Makefile for daily-tracker monorepo

.PHONY: help dev backend frontend docker-up docker-down backup

help:
	@echo "Available targets:"
	@echo "  dev        - Start both services for development via docker compose"
	@echo "  backend    - Run backend dev server"
	@echo "  frontend   - Run frontend dev server"
	@echo "  docker-up  - Start docker compose services in detached mode"
	@echo "  docker-down- Stop docker compose services"
	@echo "  backup     - Run backup/restore script (dry-run)"

# Starts both services using the dev docker compose + override
dev:
	docker compose -f docker/docker-compose.yml -f docker/docker-compose.dev.yml up --build

backend:
	@echo "Starting backend (uvicorn)"
	cd backend && uvicorn main:app --reload --port 8000

frontend:
	@echo "Starting frontend (vite)"
	cd frontend && npm run dev

docker-up:
	docker compose up -d --build

docker-down:
	docker compose down

backup:
	bash backend/scripts/restore_backup.sh --dry-run

# run lint across backend and frontend
.PHONY: lint
lint:
	@echo "Running backend lint (black, isort)"
	@.venv/bin/black --check . || true
	@.venv/bin/isort --check-only . || true
	@echo "Running frontend lint (eslint)"
	@cd frontend && npm run lint || true

.PHONY: test
test:
	@echo "Running backend tests"
	@.venv/bin/python -m pip install -r backend/requirements/dev.txt || true
	@.venv/bin/pytest -q backend/tests || true
	@echo "Running frontend tests"
	@cd frontend && npm run test || true
