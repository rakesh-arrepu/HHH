# Application configuration using environment variables.
# Uses Pydantic BaseSettings to allow overrides via .env and real env vars.
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # App
    app_name: str = "daily-tracker"
    environment: str = "development"
    debug: bool = True

    # Database
    # Default to local sqlite for quick dev; override with Postgres in .env/compose
    database_url: str = "sqlite:///./app.db"

    # Security & Auth
    jwt_secret: str = "dev-secret-change-me"
    jwt_algorithm: str = "HS256"
    access_token_exp_minutes: int = 15
    refresh_token_exp_days: int = 7

    # 2FA / TOTP
    totp_issuer: str = "DailyTracker"

    # CORS
    cors_allow_origins: List[str] = ["http://localhost:3000"]
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["*"]
    cors_allow_headers: List[str] = ["*"]

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
