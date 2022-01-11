from fastapi import APIRouter

from app.schemas.proofread import (
    IIIFImageUrl,
    PageDiff,
    ProjectMetadata,
    ProofreadPage,
    VersionMetadata,
)
from app.services.diff import Diff
from app.services.proofread import DiffProofread, PechaType, Proofread

router = APIRouter()

pudrak_kunchok_tsekpa_pr = Proofread(
    project_name="pudrak_kunchok_tsekpa",
    transk="trans",
    google_ocr="trans_google",
    derge="trans_derge",
)


@router.get("/metadata/{project_name}", response_model=ProjectMetadata)
def get_project_metadata(project_name: str):
    """Return list versions"""
    proofread = DiffProofread()
    versions, prooreading_version = proofread.get_versions(project_name)
    return ProjectMetadata(versions=versions, proofreading_version=prooreading_version)


@router.get("/metadata/{project_name}/{version_name}/{vol_id}")
def get_version_metadata(project_name: str, version_name: str, vol_id: str):
    """Return list pages in the version"""
    proofread = DiffProofread()
    pages = proofread.get_pages(project_name, version_name, vol_id)
    return VersionMetadata(pages=pages)


@router.get("/{project_name}/{version_name}/{vol_id}/{page_id}")
def read_page(project_name: str, version_name: str, vol_id: str, page_id: str):
    """Return a page and image"""
    proofread = DiffProofread()
    content, img_url = proofread.get_page(project_name, version_name, vol_id, page_id)
    return ProofreadPage(content=content, image_url=img_url)


@router.put("/{project_name}/{version_name}/{vol_id}/{page_id}")
def update_page(
    project_name: str, version_name: str, page_id: str, vol_id: str, page: ProofreadPage
):
    """Update page with new content"""
    proofread = DiffProofread()
    proofread.save_page(project_name, version_name, vol_id, page_id, page.content)
    return {"success": True}


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


@router.put("/{vol_id}/{page_id}")
def update_page(vol_id: str, page_id: str, page: ProofreadPage):
    pudrak_kunchok_tsekpa_pr.save_page(vol_id, page_id, page)
    return {"success": True}


@router.post("/{vol_id}/{page_id}/diffs", response_model=PageDiff)
def get_page_diffs(
    vol_id: str, page_id: str, page: ProofreadPage, diff_with: PechaType
):
    page_diffs = pudrak_kunchok_tsekpa_pr.get_diffs(vol_id, page_id, page, diff_with)
    return PageDiff(diffs=page_diffs)


@router.post("/images/next", response_model=IIIFImageUrl)
def next_image(image: IIIFImageUrl):
    next_image_url = pudrak_kunchok_tsekpa_pr.image_manager.next_image_url(
        image.image_url
    )
    print(next_image_url)
    return IIIFImageUrl(image_url=next_image_url)


@router.post("/images/previous", response_model=IIIFImageUrl)
def previous_image(image: IIIFImageUrl):
    next_image_url = pudrak_kunchok_tsekpa_pr.image_manager.previous_image_url(
        image.image_url
    )
    return IIIFImageUrl(image_url=next_image_url)


@router.post("/images/reset/{page_id}", response_model=IIIFImageUrl)
def reset_image(page_id: str, image: IIIFImageUrl):
    reset_image_url = pudrak_kunchok_tsekpa_pr.image_manager.reset_image_url(
        page_id, image.image_url
    )
    return IIIFImageUrl(image_url=reset_image_url)
