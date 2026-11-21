from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Ritmo"
    environment: str = "development"
    public_base_url: str = "http://localhost:3000"
    api_base_url: str = "http://localhost:8000"
    jwt_secret: str = "change-me"
    jwt_expire_minutes: int = 60 * 24 * 7

    database_url: str = "postgresql+asyncpg://ritmo:ritmo@localhost:5432/ritmo"

    telegram_bot_token: str = ""
    telegram_bot_username: str = ""
    telegram_webhook_secret: str = "change-me"
    mini_app_url: str = "http://localhost:3000"

    openweather_api_key: str = ""
    digest_default_hour: int = 8
    digest_default_minute: int = 0

    free_habit_limit: int = 3
    free_bill_limit: int = 3


@lru_cache
def get_settings() -> Settings:
    return Settings()
