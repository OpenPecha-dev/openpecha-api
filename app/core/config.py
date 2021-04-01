import logging
import secrets
from functools import lru_cache
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, BaseSettings, PostgresDsn, validator

log = logging.getLogger("unvicorn")


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    API_V1_VERSION: str = "0.2.1"
    SECRET_KEY: str = secrets.token_urlsafe(32)

    PROJECT_NAME: str
    ENVIRONMENT: str

    GITHUB_ACCESS_TOKEN_URL: str = "https://github.com/login/oauth/access_token"
    GITHUB_OAUTH_CLIENT_ID: str
    GITHUB_OAUTH_CLIENT_SECRET: str
    GITHUB_TOKEN: str

    BACKEND_CORS_ORIGINS: List[AnyHttpUrl]

    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
