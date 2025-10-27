from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List
from functools import lru_cache

class Settings(BaseSettings):
    API_PREFIX: str
    API_VERSION: str
    DEBUG: bool
    SQLALCHEMY_DATABASE_URL: str
    ALLOWED_ORIGINS: str
    JWT_SECRET: str
    JWT_ALGORITHM: str
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASSWORD: str

    @field_validator("ALLOWED_ORIGINS")
    def parse_allowed_origins(cls, v: str) -> List[str]:
        return v.split(',') if v else []
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

@lru_cache()
def get_settings() -> Settings:
    return Settings()
