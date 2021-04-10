from typing import Generator

from fastapi import Depends, Header, HTTPException, status
from github import Github, GithubException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.db.session import SessionLocal


def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_current_user(
    db: Session = Depends(get_db), token: str = Header(...)
) -> models.User:
    try:
        gh_user = Github(token).get_user()
    except GithubException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = crud.user.get(db, id=gh_user.id)
    if not user:
        user = schemas.UserCreate(
            id=gh_user.id, username=gh_user.login, email=gh_user.email
        )
        crud.user.create(db, obj_in=user)
    return user


def get_current_active_superuser(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if not crud.user.is_superuser(current_user):
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user
