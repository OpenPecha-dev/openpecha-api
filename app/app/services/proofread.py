from typing import Dict

from openpecha.config import BASE_PATH

from app.schemas.pecha import Page
from app.schemas.proofread import ProofreadPage


def path2names(paths):
    return [path.stem for path in paths]


def list_sorted_paths_name(path):
    return path2names(sorted((path.iterdir())))


class ImageManager:
    """
    Issue correct image to the specific page text
    """

    def __init__(self, base_path):
        self.offset_info_path = base_path / "offset_info.json"

    def get_image_url(self, vold_id: str, page_id: str):
        return "https://iiif.bdrc.io/bdr:I1KG14011::I1KG140110100.jpg/full/max/0/default.jpg"


class Proofread:
    """
    Proofread class prepare and serve pages to be proof read.

    Args:
        transk (str): transkribus pecha id
        google_ocr (str): google ocred pecha id
        derge (str): derge pecha id
    """

    def __init__(self, project_name, transk, google_ocr, derge):
        self.project_name = project_name
        self.transkribus = transk
        self.google_ocr = google_ocr
        self.derge = derge
        self.base_path = BASE_PATH / "proofread" / self.project_name
        self.image_manager = ImageManager(self.base_path)

    def get_vols_metadata(self) -> Dict[str, str]:
        vols = list_sorted_paths_name(self.base_path / self.transkribus)
        return {"vols": vols}

    def get_pages_metadata(self, vol_id: str):
        pages = list_sorted_paths_name(self.base_path / self.transkribus / vol_id)
        return {"pages": pages}

    def get_page(self, vol_id: str, page_id: str):
        page_fn = self.base_path / self.transkribus / vol_id / f"{page_id}.txt"
        if not page_fn.is_file():
            return ""
        return page_fn.read_text()

    def get_image_url(self, vol_id: str, page_id: str):
        image_url = self.image_manager.get_image_url(vol_id, page_id)
        return image_url

    def get_diffs(self, vol_id: str, page_id: str, page: ProofreadPage):
        pass
