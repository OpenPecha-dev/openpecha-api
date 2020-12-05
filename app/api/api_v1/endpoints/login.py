from fastapi import APIRouter

from app.core import security

router = APIRouter()


@router.post("/login/oauth/access_token")
def login_access_token(code: str):
    """
    Github oauth web application flow, get an access token for given code
    """
    response = security.get_github_access_token(code)
    return response
