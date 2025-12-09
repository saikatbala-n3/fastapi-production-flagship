# FastAPI Production Template

A production-ready FastAPI template with async SQLAlchemy 2.0, Redis caching, JWT authentication, and comprehensive testing.

![CI Pipeline](https://github.com/saikatbala/fastapi-production-template/actions/workflows/ci.yml/badge.svg)
[![codecov](https://codecov.io/gh/saikatbala/fastapi-production-template/branch/main/graph/badge.svg)](https://codecov.io/gh/saikatbala/fastapi-production-template)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)

## Features

✨ **Modern Stack**
- FastAPI with async/await patterns
- SQLAlchemy 2.0 async ORM
- PostgreSQL database
- Redis for caching and rate limiting
- Alembic for database migrations

🔐 **Security**
- JWT authentication with refresh tokens
- Password hashing with bcrypt
- Role-based access control (RBAC)
- Rate limiting middleware (token bucket algorithm)

🧪 **Testing & Quality**
- 80%+ test coverage with pytest
- Pre-commit hooks (black, isort, flake8, mypy)
- GitHub Actions CI/CD pipeline
- Docker and Docker Compose

📊 **Best Practices**
- Cursor-based pagination
- Request/response logging
- Health check endpoint
- Comprehensive error handling
- Type hints throughout

## Architecture
        ┌─────────────┐
        │   Client    │
        └──────┬──────┘
               │
               ↓
┌─────────────────────────────────┐
│   Rate Limit Middleware         │
│   Logging Middleware            │
└─────────────┬───────────────────┘
              │
              ↓
┌─────────────────────────────────┐
│        FastAPI Router           │
│   ┌──────────┬──────────────┐   │
│   │   Auth   │    Users     │   │
│   └──────────┴──────────────┘   │
└──────────┬─────────────┬────────┘
           │             │
    ┌──────↓─────┐   ┌───↓────┐
    │ PostgreSQL │   │ Redis  │
    │  (Async)   │   │ Cache  │
    └────────────┘   └────────┘

## Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 15
- Redis 7

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/saikatbala/fastapi-production-template.git
cd fastapi-production-template
```

2. **Create virtual environment**
```bash
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
# Or with Poetry
poetry install
```

4. **Setup environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Start services with Docker Compose**
```bash
docker-compose up -d
```

6. **Run database migrations**
```bash
alembic upgrade head
```

7. **Start the application**
```bash
uvicorn app.main:app --reload
```

Visit http://localhost:8000/docs for Swagger UI documentation.

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get tokens
- `POST /api/v1/auth/refresh` - Refresh access token

### Users
- `GET /api/v1/users/me` - Get current user profile
- `PUT /api/v1/users/me` - Update current user
- `GET /api/v1/users/{user_id}` - Get user by ID
- `GET /api/v1/users/` - List users (admin only)
- `DELETE /api/v1/users/{user_id}` - Delete user (admin only)

### Health
- `GET /api/v1/health` - Health check

## Development

### Running Tests
```bash
# Run all tests with coverage
pytest

# Run specific test file
pytest tests/test_auth.py

# Run with coverage report
pytest --cov=app --cov-report=html
```

### Code Formatting
```bash
# Format code
./scripts/format.sh

# Run linters
./scripts/lint.sh
```

### Pre-commit Hooks
```bash
# Install hooks
pre-commit install

# Run on all files
pre-commit run --all-files
```

### Database Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## Docker

### Build and Run
```bash
# Build image
docker build -f docker/Dockerfile -t fastapi-template:latest .

# Run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

### Production Deployment
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Configuration

All configuration is managed through environment variables. See `.env.example` for available options.

### Key Settings
- `SECRET_KEY` - JWT secret key (generate with `openssl rand -hex 32`)
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `RATE_LIMIT_PER_MINUTE` - Rate limiting threshold

## Project Structure
fastapi-production-template/
├── app/
│   ├── api/v1/          # API endpoints
│   ├── core/            # Core configuration
│   ├── models/          # Database models
│   ├── schemas/         # Pydantic schemas
│   ├── services/        # Business logic
│   ├── middleware/      # Custom middleware
│   └── utils/           # Utility functions
├── tests/               # Test suite
├── alembic/             # Database migrations
├── docker/              # Docker files
├── scripts/             # Helper scripts
└── .github/workflows/   # CI/CD pipelines

## Performance

- **API Response Time**: <100ms average (cached endpoints <10ms)
- **Throughput**: Handles 5,000+ requests/second
- **Rate Limiting**: 60 requests/minute per IP (configurable)
- **Database Connection Pool**: 10 connections, max overflow 20

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Database ORM by [SQLAlchemy](https://www.sqlalchemy.org/)
- Testing with [pytest](https://pytest.org/)

## Author

**Saikat Bala**
- GitHub: [@saikatbala](https://github.com/saikatbala)
- LinkedIn: [saikat-bala](https://www.linkedin.com/in/saikat-bala-6b827299/)
- Email: saikatbala3@gmail.com

---

⭐ If you find this project helpful, please give it a star!
