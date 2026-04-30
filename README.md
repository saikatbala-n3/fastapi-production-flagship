# FastAPI Production API

Async REST API with JWT authentication, Redis rate limiting, role-based access control, and Prometheus metrics.

**Stack:** FastAPI · SQLAlchemy 2.0 (async) · PostgreSQL 15 · Redis 7 · PyJWT · bcrypt · Prometheus

---

## Features

- JWT access + refresh tokens with Redis blocklist for logout
- Token bucket rate limiting (60 req/min per IP, configurable)
- Role-based access control — `user` and `admin` roles
- Correlation ID middleware for request tracing
- Prometheus metrics at `/metrics`
- Tables created on startup via `create_all` — no migration tool needed

---


## API Endpoints

### Auth
| Method | Path | Description |
|--------|------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Login, returns access + refresh tokens |
| POST | `/auth/refresh` | Exchange refresh token for new access token |
| POST | `/auth/logout` | Revoke current access token |

### Users
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/users/me` | any | Current user profile |
| PUT | `/users/me` | any | Update current user |
| GET | `/users/{user_id}` | any | Get user by ID |
| GET | `/users/` | admin | List all users |
| DELETE | `/users/{user_id}` | admin | Delete user |

### System
| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/metrics` | Prometheus metrics |

---

## Configuration

Copy `.env.example` to `.env` and set values:

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | — | Async PostgreSQL URL (`postgresql+asyncpg://...`) |
| `REDIS_URL` | — | Redis URL (`redis://...`) |
| `SECRET_KEY` | **required** | JWT signing key (`openssl rand -hex 32`) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Access token TTL |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Refresh token TTL |
| `CORS_ORIGINS` | `["http://localhost:3000"]` | Allowed origins |
| `RATE_LIMIT_PER_MINUTE` | `60` | Requests per IP per minute |

---

## Project Structure

```
app/
├── auth/           # JWT auth — register, login, refresh, logout
├── users/          # User CRUD — models, schemas, routes, service
├── core/           # Config, database session, deps, Redis cache
├── middleware/     # Rate limiting, correlation ID
└── metrics.py      # Prometheus counters and histograms
tests/
├── test_auth.py
├── test_user.py
├── test_rate_limit.py
└── test_utils.py
```
