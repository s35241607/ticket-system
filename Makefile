.PHONY: help install dev-install test lint format type-check clean docker-up docker-down docker-logs

# 預設目標
help:
	@echo "Available commands:"
	@echo "  install      - Install production dependencies"
	@echo "  dev-install  - Install development dependencies"
	@echo "  test         - Run tests"
	@echo "  test-cov     - Run tests with coverage"
	@echo "  lint         - Run linting (flake8)"
	@echo "  format       - Format code (black + isort)"
	@echo "  type-check   - Run type checking (mypy)"
	@echo "  clean        - Clean cache and build files"
	@echo "  docker-up    - Start all services with Docker Compose"
	@echo "  docker-down  - Stop all services"
	@echo "  docker-logs  - Show logs from all services"
	@echo "  pre-commit   - Install pre-commit hooks"

# 安裝依賴
install:
	pip install -r requirements.txt

dev-install: install
	pip install pre-commit
	pre-commit install

# 測試
test:
	pytest

test-cov:
	pytest --cov=src --cov-report=html --cov-report=term

# 程式碼品質
lint:
	flake8 src/ tests/

format:
	black src/ tests/
	isort src/ tests/

type-check:
	mypy src/

# 清理
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/

# Docker 操作
docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-rebuild:
	docker-compose down
	docker-compose build --no-cache
	docker-compose up -d

# 資料庫操作
db-upgrade:
	alembic upgrade head

db-downgrade:
	alembic downgrade -1

db-revision:
	alembic revision --autogenerate -m "$(message)"

# 開發服務器
dev-ticket:
	uvicorn src.backend.ticket_api.main:app --host 0.0.0.0 --port 8000 --reload

dev-knowledge:
	uvicorn src.backend.knowledge_api.main:app --host 0.0.0.0 --port 8001 --reload

# Pre-commit
pre-commit:
	pre-commit install
	pre-commit run --all-files