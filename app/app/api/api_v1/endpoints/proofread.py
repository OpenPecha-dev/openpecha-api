from typing import Dict, List

from fastapi import APIRouter
from openpecha.proofreading import get_page, get_pages_info, get_vol_info, save_page

from app.schemas.proofread import ProofreadPage

router = APIRouter()

BRANCH = "test-proofread"


@router.get("/{pecha_id}", response_model=List[Dict])
def read_vols_info(pecha_id: str):
    volumes = get_vol_info(pecha_id=pecha_id, branch=BRANCH)
    return volumes


@router.get("/{pecha_id}/{vol_id}", response_model=List[str])
def read_pages_info(pecha_id: str, vol_id: str):
    page_ids = get_pages_info(pecha_id, vol_id, branch=BRANCH)
    return page_ids


@router.get("/{pecha_id}/{vol_id}/{page_id}", response_model=ProofreadPage)
def read_page(pecha_id: str, vol_id: str, page_id: str):
    page_data = get_page(pecha_id, vol_id, page_id, branch=BRANCH)
    page = ProofreadPage(content=page_data["content"], image_url=page_data["image_url"])
    return page


@router.post("/{pecha_id}/{vol_id}/{page_id}")
def update_page(pecha_id: str, vol_id: str, page_id: str, page: ProofreadPage):
    save_page(pecha_id, vol_id, page_id, page.content, branch=BRANCH)
    return {"success": True}
