# Project Structure & Organization

## Root Directory Layout

```
├── src/                    # Source code
├── tests/                  # Test files
├── docs/                   # Documentation
├── deployment/             # Deployment configurations
├── docker-compose.yml      # Local development setup
├── Dockerfile             # Container configuration
├── requirements.txt        # Python dependencies
└── README.md              # Project overview
```

## Source Code Organization (`src/`)

The project follows **Clean Architecture** principles with clear layer separation:

### Domain Layer (`src/domain/`)

Core business logic, independent of external frameworks:

```
domain/
├── entities/              # Business entities with behavior
├── events/                # Domain events for business processes
├── repositories/          # Repository interfaces (contracts)
└── value_objects/         # Immutable value objects
```

Note: Domain exceptions may be added as the domain model evolves.

### Application Layer (`src/application/`)

Use cases and application services:

```
application/
└── use_cases/             # Business use cases
```

Note: Other application layer components (services, dtos, interfaces, events) may be added as the project evolves.

### Infrastructure Layer (`src/infrastructure/`)

External concerns and framework implementations:

```
infrastructure/
├── events/                # Event publisher implementations
└── repositories/          # Repository implementations
```

Note: Additional infrastructure components (persistence, messaging, security) will be added as needed.

### Interface Layer (`src/interface/`)

External interfaces and adapters:

```
interface/
└── api/                   # API controllers and routes
```

Note: REST endpoints, schemas, and event handlers will be organized under the api/ directory as the project grows.

### Backend Services (`src/backend/`)

Separate API services:

```
backend/
├── ticket_api/            # Ticket management API
│   ├── main.py            # FastAPI application
│   ├── models/            # SQLAlchemy models
│   ├── schemas/           # Pydantic schemas
│   ├── routers/           # API route handlers
│   └── dependencies.py    # Dependency injection
├── knowledge_api/         # Knowledge management API
│   └── [similar structure]
└── shared/                # Shared utilities between APIs
```

### Database Layer (`src/database/`)

Database-related configurations:

```
database/
├── models/                # SQLAlchemy model definitions
├── schemas/               # Database schema definitions
├── migrations/            # Alembic migration files
├── db.py                  # Database connection setup
└── session.py             # Database session management
```

### Frontend (`src/frontend/`)

Vue.js frontend applications:

```
frontend/
├── ticket/                # Ticket system frontend
├── knowledge/             # Knowledge system frontend
└── shared/                # Shared components and utilities
```

### Utilities (`src/utils/`)

Cross-cutting concerns:

```
utils/
├── dependencies.py        # FastAPI dependencies
├── exceptions.py          # Custom exception classes
├── helpers.py             # Utility functions
├── logger.py              # Logging configuration
├── middleware.py          # Custom middleware
└── security.py            # Authentication and authorization
```

## Test Structure (`tests/`)

Tests mirror the source structure:

```
tests/
├── application/           # Application layer tests
├── backend/               # API endpoint tests
├── domain/                # Domain logic tests
├── integration/           # Integration tests
├── conftest.py            # Pytest configuration and fixtures
└── [mirrors src/ structure]
```

## Documentation (`docs/`)

Comprehensive project documentation:

```
docs/
├── PRD.md                           # Product requirements
├── Roadmap.md                       # Development roadmap
├── clean_architecture_design.md     # Architecture documentation
├── tdd_implementation_guide.md      # TDD guidelines
├── Metrics_Framework.md             # Performance metrics
└── [system-specific docs]
```

## Deployment (`deployment/`)

Infrastructure and deployment configurations:

```
deployment/
├── docker/                # Docker configurations
├── kubernetes/            # K8s manifests
├── scripts/               # Deployment scripts
└── README.md              # Deployment instructions
```

## Naming Conventions

### Files and Directories

- Use **snake_case** for Python files and directories
- Use **kebab-case** for documentation files
- Use descriptive names that indicate purpose

### Code Structure

- **Entities**: Singular nouns (e.g., `Document`, `User`)
- **Use Cases**: Verb phrases (e.g., `CreateDocument`, `UpdateTicket`)
- **Repositories**: Entity + Repository (e.g., `DocumentRepository`)
- **Services**: Entity + Service (e.g., `DocumentService`)

### Database Models

- Table names: plural snake_case (e.g., `documents`, `user_roles`)
- Column names: snake_case (e.g., `created_at`, `user_id`)
- Foreign keys: `{table}_id` (e.g., `user_id`, `category_id`)

## Import Organization

Follow this import order:

1. Standard library imports
2. Third-party library imports
3. Local application imports (domain → application → infrastructure → interface)

Example:

```python
# Standard library
from datetime import datetime
from typing import List, Optional

# Third-party
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

# Local - Domain
from ...domain.entities.document import Document
from ...domain.repositories.document_repository import DocumentRepository

# Local - Application
from ...application.use_cases.create_document import CreateDocumentUseCase

# Local - Infrastructure
from ...infrastructure.database import get_db
```

## Configuration Management

- Environment-specific settings in `src/config.py`
- Use Pydantic for configuration validation
- Environment variables for sensitive data
- Default values for development convenience

## Key Principles

1. **Dependency Rule**: Dependencies point inward (toward domain)
2. **Single Responsibility**: Each module has one reason to change
3. **Interface Segregation**: Small, focused interfaces
4. **Dependency Inversion**: Depend on abstractions, not concretions
5. **Separation of Concerns**: Clear boundaries between layers
