from typing import Generator

from fastapi import Header, HTTPException
from github import Github, GithubException

from app.db.session import SessionLocal
from app.schemas.user import User


def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_user(token: str = Header(...)) -> User:
    try:
        user = Github(token).get_user()
        return User(id=user.id, username=user.login, email=user.email)
    except GithubException:
        raise HTTPException(status_code=401, detail="Requires authentication")
