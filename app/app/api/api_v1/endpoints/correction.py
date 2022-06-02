from typing import List

from fastapi import APIRouter

from app.services.symspell import symspell_lookup

router = APIRouter()


@router.get("", response_model=List[str])
def get_candidates(word: str, n: int = 10):
    return symspell_lookup.get_candidates(word, n=n)
