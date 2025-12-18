import os
from functools import lru_cache

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    api_prefix: str = Field("/api", description="Base API prefix for routing")
    log_level: str = Field("INFO", description="Logging level")
    default_confidence_threshold: int = Field(50, description="Default confidence cutoff")

    class Config:
        env_prefix = "SPORTS_PREDICTOR_"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    return Settings()


def get_logger(name: str):
    import logging

    settings = get_settings()
    logging.basicConfig(level=settings.log_level)
    return logging.getLogger(name)
