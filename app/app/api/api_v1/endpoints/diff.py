from typing import List

from fastapi import APIRouter

from app.schemas.diff import DiffInput
from app.services.diff import Diff

router = APIRouter()


@router.post("/", response_model=List[list])
def find_diffs(input: DiffInput):
    diff = Diff(input.textA, input.textB)
    return diff.compute()
