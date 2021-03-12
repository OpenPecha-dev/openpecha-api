import logging
from functools import lru_cache
from typing import List, Union

from environs import Env
from pydantic import AnyHttpUrl, BaseSettings, validator

env = Env()
env.read_env()
log = logging.getLogger("unvicorn")


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    API_V1_VERSION: str = "0.2.0"

    PROJECT_NAME: str = "openpecha-api"
    ENVIRONMENT: str = env.str("ENVIRONMENT", "dev")  # dev, stage, prod
    TESTING: bool = env.bool("TESTING", False)  # in test mode or not

    GITHUB_ACCESS_TOKEN_URL: str = "https://github.com/login/oauth/access_token"
    GITHUB_OAUTH_CLIENT_ID: str = env.str("GITHUB_OAUTH_CLIENT_ID")
    GITHUB_OAUTH_CLIENT_SECRET: str = env.str("GITHUB_OAUTH_CLIENT_SECRET")
    GITHUB_TOKEN: str = env.str("GITHUB_TOKEN")

    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = env.str("BACKEND_CORS_ORIGINS")


@lru_cache()
def get_settings() -> BaseSettings:
    log.info("Loading config settings from the environment...")
    return Settings()
