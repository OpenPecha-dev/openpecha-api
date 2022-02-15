from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from openpecha.core.annotations import Span
from openpecha.core.layer import Layer, LayerEnum, PechaMetaData, SpanINFO
from sqlalchemy.orm import Session

from app import crud, schemas
from app.api import deps
from app.core.slack_gateway import slack_gateway
from app.services.pechas import (
    ExportFormat,
    create_editor_content_from_pecha,
    create_export,
    create_opf_pecha,
    delete_opf_pecha,
    get_pecha,
    update_base_layer,
    update_pecha_assets,
    update_pecha_with_editor_content,
)

router = APIRouter()


@router.get("", response_model=List[schemas.pecha.Pecha])
async def read_pecha(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: schemas.user.User = Depends(deps.get_current_user),
):
    """
    Retrieve pechas.
    """
    if crud.user.is_superuser(current_user):
        pechas = crud.item.get_multi(db, skip=skip, limit=limit)
    else:
        pechas = crud.pecha.get_multi_by_owner(
            db=db, owner_id=current_user.id, skip=skip, limit=limit
        )
    return pechas


def create_pecha_obj(pecha_id, title, image_fn):
    return {
        "id": pecha_id,
        "title": title,
        "img": f"https://github.com/OpenPecha/{pecha_id}/raw/master/{pecha_id}.opf/assets/image/{image_fn}",
    }


@router.post("")
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
    current_user: schemas.user.User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    """
    Create new pecha
    """
    pecha_id, front_cover_image_fn = await create_opf_pecha(
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

    pecha_obj = create_pecha_obj(pecha_id, title, front_cover_image_fn.name)
    pecha = crud.pecha.create_with_owner(
        db=db, obj_in=pecha_obj, owner_id=current_user.id
    )

    slack_gateway.send_message(
        "\N{party popper} " + f"new pecha {pecha.id} created by {current_user.username}"
    )
    return {"pecha_id": pecha.id}


@router.delete("/{id}")
async def delete_pecha(
    *,
    db: Session = Depends(deps.get_db),
    id: str,
    current_user: schemas.user.User = Depends(deps.get_current_user),
) -> Any:
    """
    Delete a pecha
    """
    pecha = crud.pecha.get(db=db, id=id)
    if not pecha:
        raise HTTPException(status_code=404, detail="Pecha not found")
    if pecha.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Not enough Permission")
    delete_opf_pecha(id)
    pecha = crud.pecha.remove(db=db, id=id)
    return pecha


@router.get("/{pecha_id}/components", response_model=Dict[str, List[LayerEnum]])
def read_components(pecha_id: str):
    pecha = get_pecha(pecha_id)
    return pecha.components


@router.get("/{pecha_id}/base/{base_name}", response_model=str)
def read_base(pecha_id: str, base_name):
    pecha = get_pecha(pecha_id)
    return pecha.get_base(base_name)


@router.post("/{pecha_id}/base/{base_name}", status_code=status.HTTP_201_CREATED)
def create_base(
    pecha_id: str,
    base_name: str,
    base: schemas.pecha.BaseLayer,
    user: schemas.user.User = Depends(deps.get_current_user),
):
    """
    Create new base layer.
    """
    pecha = get_pecha(pecha_id)
    pecha.base[base_name] = base.content
    pecha.save_base()
    return {"success": True}


@router.put("/{pecha_id}/base/{base_name}")
def update_base(
    pecha_id: str,
    base_name: str,
    updated_base: schemas.pecha.BaseLayer,
    layers: List[Layer],
    user: schemas.user.User = Depends(deps.get_current_user),
):
    """
    Update base and corresponding layers also updated.
    """
    updated_layers = update_base_layer(
        pecha_id, base_name, updated_base.content, list(map(lambda x: x.dict(), layers))
    )
    return {"base": updated_base.content, "layers": updated_layers}


@router.delete("/{pecha_id}/base/{base_name}", response_model=str)
def delete_base(
    pecha_id: str,
    base_name: str,
    user: schemas.user.User = Depends(deps.get_current_user),
):
    raise HTTPException(status_code=501, detail="Endpoint not functional yet")


@router.get("/{pecha_id}/layers/{base_name}", response_model=List[Layer])
def read_layers(pecha_id: str, base_name: str):
    raise HTTPException(status_code=501, detail="Endpoint not functional yet")


@router.get("/{pecha_id}/layers/{base_name}/{layer_name}", response_model=Layer)
def read_layer(pecha_id: str, base_name, layer_name: str):
    pecha = get_pecha(pecha_id)
    return pecha.get_layer(base_name, LayerEnum(layer_name))


@router.post("/{pecha_id}/layers/{base_name}/{layer_name}", response_model=Layer)
def create_layer(
    pecha_id: str,
    base_name: str,
    layer_name: str,
    layer: Layer,
    user: schemas.user.User = Depends(deps.get_current_user),
):
    pecha = get_pecha(pecha_id)
    pecha.layers[base_name][LayerEnum(layer_name)] = layer
    pecha.save_layers()
    return {"success": True}


@router.put("/{pecha_id}/layers/{base_name}/{layer_name}")
def update_layer(
    pecha_id: str,
    base_name,
    layer_name: str,
    layer: Layer,
    user: schemas.user.User = Depends(deps.get_current_user),
):
    pecha = get_pecha(pecha_id)
    pecha.save_layer(base_name, layer_name, layer)
    return {"success": True}


@router.delete("/{pecha_id}/layers/{base_name}/{layer_name}", response_model=Layer)
def delete_layer(
    pecha_id: str,
    base_name: str,
    layer_name,
    user: schemas.user.User = Depends(deps.get_current_user),
):
    raise HTTPException(status_code=501, detail="Endpoint not functional yet")


@router.get("/{pecha_id}/export/{branch}")
def export_pecha(
    pecha_id: str,
    branch: str = "master",
    format: ExportFormat = ExportFormat.epub,
    user: schemas.user.User = Depends(deps.get_current_user),
):
    download_link = create_export(pecha_id, branch, format)
    return {"download_link": download_link}


@router.get("/{pecha_id}/{base_name}/editor")
def get_editor_content(
    pecha_id: str,
    base_name: str,
    user: schemas.user.User = Depends(deps.get_current_user),
):
    return {"content": create_editor_content_from_pecha(pecha_id, base_name)}


@router.put("/{pecha_id}/{base_name}/editor")
def update_pecha(
    pecha_id: str,
    base_name: str,
    editor_content: schemas.pecha.EditorContent,
    user: schemas.user.User = Depends(deps.get_current_user),
):
    # try:
    update_pecha_with_editor_content(pecha_id, base_name, editor_content.content)
    # except Exception as e:
    #     print(e)
    #     return {"success": False}
    return {"success": True}


@router.get("/{pecha_id}/metadata", response_model=PechaMetaData)
def read_metadata(*, pecha_id: str):
    pecha = get_pecha(pecha_id)
    pecha.meta.id
    return pecha.meta


@router.put("/{pecha_id}/metadata")
def update_metadata(
    *,
    pecha_id: str,
    metadata: PechaMetaData,
    # front_cover_image: Optional[UploadFile] = File(None),
    # publication_data_image: Optional[UploadFile] = File(None),
    db: Session = Depends(deps.get_db),
    current_user: schemas.user.User = Depends(deps.get_current_user),
):
    pecha_db = crud.pecha.get(db, id=pecha_id)
    if not pecha_db:
        raise HTTPException(status_code=404, detail="Pecha not found")
    if pecha_db.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Not enough Permission")

    pecha_opf = get_pecha(pecha_id)

    # check if metadata is changed
    if pecha_opf.meta.id and pecha_opf.meta == metadata:
        return pecha_db

    # update metadata
    pecha_opf._meta = metadata
    # update assets if chagned
    # if front_cover_image.filename:
    #     asset_fn = update_pecha_assets(pecha_opf, "image", "cover", front_cover_image)
    #     pecha_opf.meta.source_metadata["cover"] = asset_fn
    # if publication_data_image.filename:
    #     asset_fn = update_pecha_assets(
    #         pecha_opf, "image", "credit", publication_data_image
    #     )
    #     pecha_opf.meta.source_metadata["credit"] = asset_fn
    pecha_opf.save_meta()

    pecha_obj = create_pecha_obj(
        pecha_id,
        title=metadata.source_metadata["title"],
        image_fn=pecha_opf.meta.source_metadata["cover"],
    )
    pecha_db = crud.pecha.update(db, db_obj=pecha_db, obj_in=pecha_obj)
    return pecha_db


@router.post("/{pecha_id}/{base_name}/span", response_model=SpanINFO)
def get_span_info(pecha_id: str, base_name: str, span: Span, layers: List[LayerEnum]):
    pecha = get_pecha(pecha_id)
    print(span, layers)
    span_info = pecha.get_span_info(base_name, span, layers)
    return span_info
