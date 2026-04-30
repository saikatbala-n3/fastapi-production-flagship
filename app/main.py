import time
import logging

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import make_asgi_app
from sqlalchemy.exc import IntegrityError

from app.core import cache
from app.core.config import settings
from app.core.database import Base, engine
from app.users.models import User
from app.users.routes import router as user_router
from app.auth.routes import router as auth_router
from app.metrics import http_duration, http_requests
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.correlation_id import CorrelationIdMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await cache.connect()
    yield
    await cache.disconnect()
    await engine.dispose()


app = FastAPI(
    title="FastAPI Production API",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def record_metric(request: Request, call_next):
    """Record HTTP request count and duration for Prometheus."""
    start = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start
    http_requests.labels(
        method=request.method, path=request.url.path, status=response.status_code
    ).inc()
    http_duration.observe(duration)
    return response


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    """Catch DB unique constraint violations globally — returns 409."""
    return JSONResponse(status_code=409, content={"detail": "Resource already exists"})


app.include_router(auth_router)
app.include_router(user_router)

app.mount("/metrics", make_asgi_app())


@app.get("/health")
async def health():
    return {"status": "healthy"}
