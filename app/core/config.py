from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://api:api@postgres_n3:5432/production_api"
    redis_url: str = "redis://redis_n3:6379/0"

    secret_key: str
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    cors_origins: list[str] = ["http://localhost:3000"]
    rate_limit_per_minute: int = 60

    model_config = {"env_file": ".env"}


settings = Settings()
