from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    azure_api_key: str = ""
    azure_endpoint: Optional[str] = None
    frontend_app_url: Optional[str] = None
    database_url: Optional[str] = None
    chroma_tenant: str = ""
    chroma_database: str = ""
    chroma_api_key: str = ""
    google_client_id: str = ""
    google_client_secret: str = ""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
