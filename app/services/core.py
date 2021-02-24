from fastapi import UploadFile
from openpecha.blupdate import Blupdate, update_ann_layer
from openpecha.cli import download_pecha

from app.utils import save_upload_file_tmp


def create_opf_pecha(
    title: str,
    subtitle: str,
    author: str,
    collection: str,
    publisher: str,
    front_cover_image: UploadFile,
    publication_data_image: UploadFile,
):
    front_cover_image_fn = save_upload_file_tmp(front_cover_image)
    publication_data_image_fn = save_upload_file_tmp(publication_data_image)
    print(front_cover_image_fn)
    print(publication_data_image_fn)
    return "P000200"


def get_old_base(pecha_id, base_id):
    pecha_path = download_pecha(pecha_id, needs_update=False)
    if base_id[0] == "v":
        base_fn = pecha_path / f"{pecha_id}.opf" / "base" / f"{base_id}.txt"
        return base_fn.read_text(encoding="utf-8")


def update_base_layer(pecha_id, new_base, layers):
    old_base = get_old_base(pecha_id, new_base.id)
    updater = Blupdate(old_base, new_base)
    for layer in layers:
        update_ann_layer(layer, updater)
    return layers
