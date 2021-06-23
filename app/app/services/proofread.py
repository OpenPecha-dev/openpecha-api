from typing import Dict

from openpecha.config import BASE_PATH


def path2names(paths):
    return [path.stem for path in paths]


def list_sorted_paths_name(path):
    return path2names(sorted((path.iterdir())))


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

    def get_vols_metadata(self) -> Dict[str, str]:
        vols = list_sorted_paths_name(self.base_path / self.transkribus)
        return {"vols": vols}

    def get_pages_metadata(self, vol_id: str):
        pages = list_sorted_paths_name(self.base_path / self.transkribus / vol_id)
        return {"pages": pages}
