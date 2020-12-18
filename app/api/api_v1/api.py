from fastapi import APIRouter

from app.api.api_v1.endpoints import editor, login

api_router = APIRouter()
api_router.include_router(login.router, tags=["Login"])
api_router.include_router(editor.router, tags=["Editor"])
