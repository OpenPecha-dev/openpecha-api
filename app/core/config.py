from environs import Env
from pydantic import BaseSettings

env = Env()
env.read_env()


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"

    PROJECT_NAME: str = "openpecha-api"

    GITHUB_ACCESS_TOKEN_URL: str = "https://github.com/login/oauth/access_token"
    GITHUB_OAUTH_CLIENT_ID: str = env.str("GITHUB_OAUTH_CLIENT_ID")
    GITHUB_OAUTH_CLIENT_SECRET: str = env.str("GITHUB_OAUTH_CLIENT_SECRET")


settings = Settings()
