from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    APP_NAME: str = 'QUASAR AI'
    APP_ENV: str = 'development'
    APP_HOST: str = '0.0.0.0'
    APP_PORT: int = 8000
    API_V1_PREFIX: str = '/api/v1'

    DATABASE_URL: str = 'postgresql+asyncpg://quasar:quasar@db:5432/quasar'
    ALEMBIC_DATABASE_URL: str = 'postgresql+psycopg://quasar:quasar@db:5432/quasar'

    REDIS_URL: str = 'redis://redis:6379/0'

    JWT_SECRET_KEY: str = 'please-change-in-production'
    JWT_ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    LOG_LEVEL: str = 'INFO'


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
