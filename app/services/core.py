import tempfile

from fastapi import UploadFile
from openpecha.blupdate import Blupdate, update_ann_layer
from openpecha.catalog.manager import CatalogManager
from openpecha.cli import download_pecha
from openpecha.formatters.empty import EmptyEbook
from openpecha.github_utils import create_release
from openpecha.serializers import EpubSerializer

from app.core.config import get_settings
from app.utils import save_upload_file_tmp

settings = get_settings()


async def create_opf_pecha(
    text_file: UploadFile,
    title: str,
    subtitle: str,
    author: str,
    collection: str,
    publisher: str,
    sku: str,
    front_cover_image: UploadFile,
    publication_data_image: UploadFile,
):
    front_cover_image_fn = save_upload_file_tmp(front_cover_image)
    publication_data_image_fn = save_upload_file_tmp(publication_data_image)

    metadata = {
        "title": title,
        "subtitle": subtitle,
        "authors": [author],
        "collection": collection,
        "publisher": publisher,
        "id": sku,
        "cover": front_cover_image.filename,
        "credit": publication_data_image.filename,
    }

    assets = {"image": [front_cover_image_fn, publication_data_image_fn]}

    catalog = CatalogManager(formatter=EmptyEbook(metadata=metadata, assets=assets))
    text = await text_file.read()
    catalog.add_empty_item(text.decode("utf-8"))
    catalog.update()
    return catalog.formatter.pecha_path.name


def get_old_base(pecha_id, base_id):
    pecha_path = download_pecha(pecha_id, needs_update=False)
    if base_id[0] == "v":
        base_fn = pecha_path / f"{pecha_id}.opf" / "base" / f"{base_id}.txt"
        return base_fn.read_text(encoding="utf-8")


def update_base_layer(pecha_id, basename, new_base, layers):
    old_base = get_old_base(pecha_id, basename)
    updater = Blupdate(old_base, new_base)
    for layer in layers:
        update_ann_layer(layer, updater)
    return layers


def create_export(pecha_id: str, branch):
    pecha_path = download_pecha(pecha_id, branch=branch)
    serializer = EpubSerializer(opf_path=pecha_path / f"{pecha_path.name}.opf")

    with tempfile.TemporaryDirectory() as tmpdirname:
        export_fn = serializer.serialize(output_path=tmpdirname)
        download_url = create_release(
            pecha_id,
            prerelease=True if branch == "review" else False,
            asset_paths=[export_fn],
            token=settings.GITHUB_TOKEN,
        )
    return download_url
