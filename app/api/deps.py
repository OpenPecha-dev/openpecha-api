from fastapi import Header, HTTPException
from github import Github, GithubException

from app.schemas.core import User


def get_user(token: str = Header(...)) -> User:
    try:
        user = Github(token).get_user()
        return User(id=user.id, username=user.login, email=user.email)
    except GithubException:
        raise HTTPException(status_code=401, detail="Requires authentication")
