from fastapi import APIRouter

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
