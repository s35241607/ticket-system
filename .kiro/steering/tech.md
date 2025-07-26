# Technology Stack & Build System

## Core Technologies

### Backend Framework

- **FastAPI** - Primary API framework for high-performance async operations
- **Python 3.10** - Runtime environment
- **SQLAlchemy 2.0** - ORM with async support
- **Alembic** - Database migrations
- **Pydantic v1** - Data validation and serialization (v1.10.7)

### Database & Storage

- **PostgreSQL 16** - Primary relational database
- **Redis** - Caching and session storage
- **Elasticsearch 8.7** - Full-text search engine

### Frontend

- **Vite + Vue 3** - Modern frontend build system and framework
- **TypeScript** - Type-safe JavaScript development (planned)

### Infrastructure

- **Docker & Docker Compose** - Containerization and local development
- **KONG API Gateway** - API management and routing (planned)
- **Kafka** - Message queue for event-driven architecture (planned)

### Security & Authentication

- **JWT** - Token-based authentication (python-jose)
- **bcrypt** - Password hashing
- **SSO integration** - Single sign-on support (planned)

### Development Tools

- **pytest** - Testing framework with async support
- **black** - Code formatting
- **isort** - Import sorting
- **flake8** - Code linting
- **mypy** - Static type checking
- **mkdocs** - Documentation generation

## Architecture Patterns

### Clean Architecture

- **Domain Layer**: Entities, value objects, domain events, repository interfaces
- **Application Layer**: Use cases, application services, DTOs
- **Infrastructure Layer**: Database implementations, external service integrations
- **Interface Layer**: REST API controllers, event handlers

### Event-Driven Design

- Domain events for business logic decoupling
- Event publishers and handlers for cross-cutting concerns
- Async event processing for performance

### Test-Driven Development (TDD)

- Red-Green-Refactor cycle
- Unit tests for domain logic
- Integration tests for repositories and APIs
- End-to-end tests for complete workflows

## Common Commands

### Development Setup

```bash
# Start all services
docker-compose up -d

# Install Python dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start Ticket API (development)
uvicorn src.backend.ticket_api.main:app --host 0.0.0.0 --port 8000 --reload

# Start Knowledge API (development)
uvicorn src.backend.knowledge_api.main:app --host 0.0.0.0 --port 8001 --reload
```

### Testing

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/domain/entities/test_document.py

# Run tests in parallel
pytest -n auto
```

### Database Operations

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Code Quality

```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/
```

## Development Guidelines

### API Development

- Use FastAPI dependency injection for database sessions and services
- Follow RESTful conventions for endpoint design
- Implement proper error handling with HTTP status codes
- Use Pydantic models for request/response validation

### Database Design

- Use SQLAlchemy declarative models
- Implement proper foreign key relationships
- Add database indexes for frequently queried fields
- Use database constraints for data integrity

### Testing Strategy

- Write tests before implementation (TDD)
- Use pytest fixtures for test data setup
- Mock external dependencies in unit tests
- Use TestClient for API endpoint testing

### Code Organization

- Follow clean architecture layer separation
- Keep domain logic independent of frameworks
- Use dependency injection for loose coupling
- Implement repository pattern for data access
