from typing import List, Optional

from fastapi import APIRouter, File, UploadFile

from app import schemas
from app.services.pechas import create_export, create_opf_pecha, update_base_layer
from app.services.text_obj.texts import get_text_obj

router = APIRouter()


@router.post("/pechas")
async def create_pecha(
    title: str,
    author: str,
    sku: str,
    subtitle: Optional[str] = "",
    collection: Optional[str] = "",
    publisher: Optional[str] = "",
    text_file: UploadFile = File(...),
    front_cover_image: UploadFile = File(...),
    publication_data_image: UploadFile = File(...),
):
    pecha_id = await create_opf_pecha(
        text_file,
        title,
        subtitle,
        author,
        collection,
        publisher,
        sku,
        front_cover_image,
        publication_data_image,
    )
    return {"pecha_id": pecha_id}


@router.get("/{pecha_id}/texts/{text_id}", response_model=schemas.Text)
def read_text(pecha_id: str, text_id: str, page_no: Optional[int] = None):
    text = get_text_obj(pecha_id, text_id)
    return text


@router.get("/{pecha_id}/base/{basename}")
def read_base():
    pass


@router.put("/{pecha_id}/base/{basename}")
def update_base(
    pecha_id: str,
    basename: str,
    updated_base: schemas.core.BaseLayer,
    layers: List[schemas.core.AnnLayer],
):
    updated_layers = update_base_layer(
        pecha_id,
        updated_base.id,
        updated_base.content,
        list(map(lambda x: x.dict(), layers)),
    )
    return updated_base, updated_layers


@router.get("/{pecha_id}/export/{branch}")
def export_pecha(pecha_id: str, branch: str = "master"):
    download_link = create_export(pecha_id, branch)
    return {"download_link": download_link}
