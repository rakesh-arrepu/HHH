# config placeholder
from pydantic import BaseSettings


class Settings(BaseSettings):
    app_name: str = "daily-tracker"


settings = Settings()
