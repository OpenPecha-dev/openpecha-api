from fastapi import APIRouter

from app.services.proofread import Proofread

router = APIRouter()

proofread = Proofread("P000789", "P000005", "P000001")


@router.get("/{base_name}")
def read_base(base_name: str):
    pass
