from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./geoshield.db"
    ip2location_api_key: str = ""
    ip2location_api_url: str = "https://api.ip2location.io/"

    model_config = SettingsConfigDict(env_prefix="GEOSHIELD_", env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
