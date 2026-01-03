# Application configuration using environment variables.
# Uses Pydantic BaseSettings to allow overrides via .env and real env vars.
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional


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
    cors_allow_origins: List[str] = ["http://localhost:5173", "http://localhost:5174"]
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["*"]
    cors_allow_headers: List[str] = ["*"]

    # Cookies/CSRF
    csrf_cookie_name: str = "hhh_csrf"
    csrf_header_name: str = "X-CSRF-Token"
    cookie_domain: Optional[str] = "localhost"
    secure_cookies: bool = False
    access_cookie_name: str = "hhh_at"
    refresh_cookie_name: str = "hhh_rt"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False
    )


settings = Settings()

if settings.environment.lower() == "production":
    settings.cors_allow_origins.append("https://rakesh-arrepu.github.io")
    settings.secure_cookies = True
    settings.cookie_domain = None
