# FastAPI Project - Backend

## Architecture Overview

This FastAPI project follows a **Domain-Driven Design (DDD)** architecture with clean separation of concerns. The codebase is organized into distinct layers that promote maintainability, testability, and scalability.

### Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│                     API Layer                               │
│  ┌─────────────────┐  ┌─────────────────┐                  │
│  │   Routes        │  │   Dependencies  │                  │
│  │   (FastAPI)     │  │   (Security)    │                  │
│  └─────────────────┘  └─────────────────┘                  │
└─────────────────────────────────────────────────────────────┘
                               │
┌─────────────────────────────────────────────────────────────┐
│                   Domain Layer                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │    Services     │  │    Schemas      │  │   Models     │ │
│  │ (Business Logic)│  │ (API Contracts) │  │ (Database)   │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
│  ┌─────────────────┐                                        │
│  │  Repositories   │                                        │
│  │ (Data Access)   │                                        │
│  └─────────────────┘                                        │
└─────────────────────────────────────────────────────────────┘
                               │
┌─────────────────────────────────────────────────────────────┐
│                Infrastructure Layer                         │
│  ┌─────────────────┐  ┌─────────────────┐                  │
│  │   Database      │  │   Configuration │                  │
│  │   (PostgreSQL)  │  │   (Settings)    │                  │
│  └─────────────────┘  └─────────────────┘                  │
└─────────────────────────────────────────────────────────────┘
```

### Project Structure

```
app/
├── main.py                     # Application entry point
├── api/                        # API Layer
│   ├── main.py                 # API router configuration
│   └── routes/                 # API endpoints
│       ├── login.py            # Authentication endpoints
│       └── users.py            # User management endpoints
├── core/                       # Infrastructure Layer
│   ├── config.py               # Application settings
│   ├── db.py                   # Database connection
│   ├── deps.py                 # Dependency injection
│   └── security.py             # Authentication & security
├── domain/                     # Domain Layer (Business Logic)
│   ├── models/                 # Database models (SQLModel)
│   │   ├── token.py            # JWT token models
│   │   └── users.py            # User database model
│   ├── schemas/                # API contracts (Pydantic)
│   │   └── users.py            # User API schemas
│   ├── services/               # Business logic layer
│   │   ├── auth_service.py     # Authentication business logic
│   │   └── user_service.py     # User business logic
│   └── repositories/           # Data access layer
│       └── users_repository.py # User data operations
├── alembic/                    # Database migrations
└── tests/                      # Test suite
```

## Key Architecture Principles

### 1. **Domain-Driven Design (DDD)**
- **Domain Layer**: Contains business logic, models, and rules
- **Application Layer**: Orchestrates domain operations
- **Infrastructure Layer**: Handles external concerns (database, config)

### 2. **Clean Architecture**
- **Dependency Inversion**: Inner layers don't depend on outer layers
- **Separation of Concerns**: Each layer has a specific responsibility
- **Testability**: Business logic is isolated and easily testable

### 3. **Repository Pattern**
- Abstracts data access operations
- Makes the application database-agnostic
- Facilitates testing with mock implementations

### 4. **Service Layer**
- Encapsulates business logic and rules
- Coordinates between repositories
- Handles complex business operations

## Technology Stack

- **Framework**: FastAPI with Pydantic v2
- **Database**: PostgreSQL with SQLModel (SQLAlchemy 2.0)
- **Authentication**: JWT tokens with bcrypt password hashing
- **Migrations**: Alembic
- **Testing**: Pytest
- **Code Quality**: Ruff (linting), MyPy (type checking)
- **Dependency Management**: UV

## Requirements

* [Docker](https://www.docker.com/).
* [uv](https://docs.astral.sh/uv/) for Python package and environment management.

## Docker Compose

Start the local development environment with Docker Compose following the guide in [../development.md](../development.md).

## Development Setup

By default, the dependencies are managed with [uv](https://docs.astral.sh/uv/), go there and install it.

From the project root you can install all the dependencies with:

```console
$ uv sync
```

Then you can activate the virtual environment with:

```console
$ source .venv/bin/activate
```

Make sure your editor is using the correct Python virtual environment, with the interpreter at `.venv/bin/python`.

### Adding New Features

When adding new features, follow the established architecture:

1. **Models**: Define database models in `app/domain/models/`
2. **Schemas**: Create API contracts in `app/domain/schemas/`
3. **Repository**: Implement data access in `app/domain/repositories/`
4. **Service**: Add business logic in `app/domain/services/`
5. **API Routes**: Create endpoints in `app/api/routes/`
6. **Tests**: Add tests in `app/tests/`

## VS Code

There are already configurations in place to run the backend through the VS Code debugger, so that you can use breakpoints, pause and explore variables, etc.

The setup is also already configured so you can run the tests through the VS Code Python tests tab.

### Test Coverage

When the tests are run, a file `htmlcov/index.html` is generated, you can open it in your browser to see the coverage of the tests.

## Migrations

As during local development your app directory is mounted as a volume inside the container, you can also run the migrations with `alembic` commands inside the container and the migration code will be in your app directory (instead of being only inside the container). So you can add it to your git repository.

Make sure you create a "revision" of your models and that you "upgrade" your database with that revision every time you change them. As this is what will update the tables in your database. Otherwise, your application will have errors.

* Start an interactive session in the backend container:

```console
$ docker compose exec backend bash
```

* Alembic is already configured to import your SQLModel models from `./backend/app/models.py`.

* After changing a model (for example, adding a column), inside the container, create a revision, e.g.:

```console
$ alembic revision --autogenerate -m "Add column last_name to User model"
```

* Commit to the git repository the files generated in the alembic directory.

* After creating the revision, run the migration in the database (this is what will actually change the database):

```console
$ alembic upgrade head
```

If you don't want to use migrations at all, uncomment the lines in the file at `./backend/app/core/db.py` that end in:

```python
SQLModel.metadata.create_all(engine)
```

and comment the line in the file `scripts/prestart.sh` that contains:

```console
$ alembic upgrade head
```

