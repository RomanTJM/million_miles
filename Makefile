.PHONY: help install dev test lint format clean docker-up docker-down db-up db-down

help:
	@echo "🚗 Auto Listings Project - Available Commands"
	@echo ""
	@echo "Development:"
	@echo "  make dev              - Start development environment (Docker)"
	@echo "  make install          - Install dependencies locally"
	@echo "  make dev-backend      - Run backend API locally"
	@echo "  make dev-scraper      - Run scraper worker locally"
	@echo "  make dev-frontend     - Run frontend dev server locally"
	@echo ""
	@echo "Testing:"
	@echo "  make test             - Run all tests"
	@echo "  make test-unit        - Run unit tests"
	@echo "  make test-integration - Run integration tests"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint             - Run linters"
	@echo "  make format           - Format code"
	@echo ""
	@echo "Database:"
	@echo "  make db-migrate       - Run Alembic migrations"
	@echo "  make db-seed          - Seed database with admin user"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-up        - Start all Docker containers"
	@echo "  make docker-down      - Stop and remove containers"
	@echo "  make docker-logs      - View Docker logs"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean            - Remove cache and build files"

# ===================== Development =====================

dev:
	docker-compose up -d --build
	@echo "✅ Application started!"
	@echo "Frontend:  http://localhost:3000"
	@echo "Backend:   http://localhost:8000"
	@echo "Docs:      http://localhost:8000/docs"

install:
	cd backend && python -m venv venv
	cd backend && source venv/bin/activate && pip install -r requirements.txt
	cd frontend && npm install

dev-backend:
	cd backend && source venv/bin/activate && uvicorn app.main:app --reload

dev-scraper:
	cd backend && source venv/bin/activate && python -m app.scrapers.worker

dev-frontend:
	cd frontend && npm run dev

# ===================== Testing =====================

test:
	cd backend && pytest -v --cov=app

test-unit:
	cd backend && pytest tests/ -m unit -v

test-integration:
	cd backend && pytest tests/ -m integration -v

# ===================== Code Quality =====================

lint:
	cd backend && pylint app/ --disable=all --enable=E,F || true
	cd frontend && npm run lint || true

format:
	cd backend && black . && isort .
	cd frontend && npx prettier --write src/

# ===================== Database =====================

db-migrate:
	cd backend && alembic upgrade head

db-seed:
	cd backend && python app/seeds.py

db-rollback:
	cd backend && alembic downgrade -1

# ===================== Docker =====================

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-ps:
	docker-compose ps

# ===================== Cleanup =====================

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type d -name dist -exec rm -rf {} +
	find . -type d -name build -exec rm -rf {} +
	find . -type d -name .venv -exec rm -rf {} +
	find ./frontend -type d -name node_modules -exec rm -rf {} +
	find . -name ".DS_Store" -delete
	@echo "✅ Cleaned!"

.DEFAULT_GOAL := help
