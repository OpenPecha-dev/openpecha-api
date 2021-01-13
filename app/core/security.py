from typing import Dict

import requests

from app.core.config import get_settings

settings = get_settings()


def get_github_access_token(code: str) -> Dict:
    response = requests.post(
        settings.GITHUB_ACCESS_TOKEN_URL,
        headers={"Accept": "application/json"},
        params={
            "client_id": settings.GITHUB_OAUTH_CLIENT_ID,
            "client_secret": settings.GITHUB_OAUTH_CLIENT_SECRET,
            "code": code,
        },
    )
    return response.json()
