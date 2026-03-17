"""Application configuration via environment variables."""
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://user:pass@localhost/ecommerce"
    REDIS_URL: str = "redis://localhost:6379"
    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]
    AWS_S3_BUCKET: str = "ecommerce-assets"
    AWS_REGION: str = "us-east-1"
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    SENDGRID_API_KEY: str = ""
    ELASTICSEARCH_URL: str = "http://localhost:9200"

    class Config:
        env_file = ".env"

settings = Settings()
