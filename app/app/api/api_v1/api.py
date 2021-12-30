from fastapi import APIRouter

from app.api.api_v1.endpoints import (
    diff,
    diffproofread,
    login,
    pechas,
    pedurma,
    proofread,
    users,
    works,
)

api_router = APIRouter()

api_router.include_router(works.router, prefix="/works", tags=["Works"])
api_router.include_router(pechas.router, prefix="/pechas", tags=["Pechas"])

api_router.include_router(pedurma.router, prefix="/pedurma", tags=["Pedurma"])

api_router.include_router(proofread.router, prefix="/proofread", tags=["Proofread"])
api_router.include_router(
    diffproofread.router, prefix="/diffproofread", tags=["DiffProofread"]
)
api_router.include_router(diff.router, prefix="/diff", tags=["Diff"])

api_router.include_router(login.router, tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
