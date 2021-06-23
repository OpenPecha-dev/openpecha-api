import pydantic
from fastapi import APIRouter
from pydantic.types import PaymentCardNumber

from app.schemas.pecha import Page
from app.schemas.proofread import PageDiff, ProofreadPage
from app.services.proofread import Proofread

router = APIRouter()

pudrak_kunchok_tsekpa_pr = Proofread(
    project_name="pudrak_kunchok_tsekpa",
    transk="P000789",
    google_ocr="P000005",
    derge="P000001",
)


@router.get("/metadata/vols")
def read_vols_metadata():
    vols_metadata = pudrak_kunchok_tsekpa_pr.get_vols_metadata()
    return vols_metadata


@router.get("/metadata/vols/{vol_id}")
def read_pages_metadata(vol_id: str):
    pages_metadata = pudrak_kunchok_tsekpa_pr.get_pages_metadata(vol_id)
    return pages_metadata


@router.get("/{vol_id}/{page_id}", response_model=ProofreadPage)
def read_page(vol_id: str, page_id: str):
    page_content = pudrak_kunchok_tsekpa_pr.get_page(vol_id, page_id)
    page_image_url = pudrak_kunchok_tsekpa_pr.get_image_url(vol_id, page_id)
    return ProofreadPage(content=page_content, image_url=page_image_url)


@router.get("/{vol_id}/{page_id}/diffs", response_model=PageDiff)
def get_page_diffs(vol_id: str, page_id: str, page: ProofreadPage):
    page_diffs = pudrak_kunchok_tsekpa_pr.get_diffs(vol_id, page_id, page)
    return PageDiff(diffs=page_diffs)