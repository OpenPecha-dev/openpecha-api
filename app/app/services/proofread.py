import json
from enum import Enum
from pathlib import Path
from typing import Dict, List

from antx.core import get_diffs
from openpecha.config import BASE_PATH

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
        self.offset_info_fn = base_path / "offset_info.json"
        self._offset_info = None
        self.vol2imagegroup_fn = base_path / "vol2imagegroup.json"
        self._vol2imagegroup = None
        self.image_url_format = (
            "https://iiif.bdrc.io/bdr:{imagegroup}::{filename}/full/max/0/default.jpg"
        )

    @property
    def offset_info(self):
        if self._offset_info:
            return self._offset_info
        return json.load(self.offset_info_fn.open())

    @property
    def vol2imagegroup(self):
        if self._vol2imagegroup:
            return self._vol2imagegroup
        return json.load(self.vol2imagegroup_fn.open())

    def __get_offset_image_num(self, page_id: str):
        return page_id

    def get_image_url(self, vol_id: str, page_id: str):
        imagegroup = self.vol2imagegroup[vol_id]
        filename = f"{imagegroup}{self.__get_offset_image_num(page_id)}.jpg"
        return self.image_url_format.format(imagegroup=imagegroup, filename=filename)

    def save_offset(self, vol_id: str, page_id: str, image_url: str):
        pass

    @staticmethod
    def __parse_image_url(image_url: str):
        imagegroup_url_chunk, filename_url_chunk = image_url.split("::")
        imagegroup = imagegroup_url_chunk.split(":")[-1]
        filename = filename_url_chunk.split("/")[0]
        return imagegroup, filename

    @staticmethod
    def __parse_filename(filename: str):
        file_stem, file_ext = filename.split(".")
        imagegroup = file_stem[:-4]
        order = int(file_stem[-4:])
        return imagegroup, order, file_ext

    def __next_filename(self, filename: str):
        imagegroup, order, file_ext = self.__parse_filename(filename)
        return f"{imagegroup}{(order+1):04}.{file_ext}"

    def __previous_filename(self, filename: str):
        imagegroup, order, file_ext = self.__parse_filename(filename)
        if order > 1:
            order -= 1
        return f"{imagegroup}{(order):04}.{file_ext}"

    def next_image_url(self, image_url: str):
        imagegroup, filename = self.__parse_image_url(image_url)
        next_filename = self.__next_filename(filename)
        return self.image_url_format.format(
            imagegroup=imagegroup, filename=next_filename
        )

    def previous_image_url(self, image_url: str):
        imagegroup, filename = self.__parse_image_url(image_url)
        previous_filename = self.__previous_filename(filename)
        return self.image_url_format.format(
            imagegroup=imagegroup, filename=previous_filename
        )


class PechaType(str, Enum):
    transk = "transk"
    google_ocr = "google_ocr"
    derge = "derge"


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
        self.base_path: Path = BASE_PATH / "proofread" / self.project_name
        self.metadata_fn: Path = self.base_path / "metadata.json"
        self._metadata: Dict = {}
        self.image_manager = ImageManager(self.base_path)

    def __load_metadata(self) -> None:
        self._metadata = json.load(self.metadata_fn.open())

    def __save_metadata(self) -> None:
        json.dump(self._metadata, self.metadata_fn.open("w"))

    def get_vols_metadata(self) -> List[str]:
        if not self.metadata_fn.is_file():
            vols = list_sorted_paths_name(self.base_path / self.transkribus)
            self._metadata = {vol: {} for vol in vols}
            self.__save_metadata()

        if not self._metadata:
            self.__load_metadata()

        return list(self._metadata.keys())

    def get_pages_metadata(self, vol_id: str):
        if not self.metadata_fn.is_file():
            self.get_vols_metadata()

        if not self._metadata:
            self.__load_metadata()

        if not self._metadata[vol_id]:
            pages = list_sorted_paths_name(self.base_path / self.transkribus / vol_id)
            self._metadata[vol_id]["pages"] = {page: {} for page in pages}
            self.__save_metadata()

        return list(self._metadata[vol_id]["pages"].keys())

    def get_page(self, vol_id: str, page_id: str, pecha_id: str = None):
        pecha_id = pecha_id if pecha_id else self.transkribus
        page_fn = self.base_path / pecha_id / vol_id / f"{page_id}.txt"
        if not page_fn.is_file():
            return ""
        return page_fn.read_text()

    def save_page(self, vol_id: str, page_id: str, page: ProofreadPage):
        page_fn = self.base_path / self.transkribus / vol_id / f"{page_id}.txt"
        if not page_fn.is_file():
            return
        page_fn.write_text(page.content)
        self.image_manager.save_offset(vol_id, page_id, page.image_url)

    def get_image_url(self, vol_id: str, page_id: str):
        image_url = self.image_manager.get_image_url(vol_id, page_id)
        return image_url

    def get_diffs(
        self, vol_id: str, page_id: str, page: ProofreadPage, diff_with: PechaType
    ):
        if diff_with == PechaType.google_ocr:
            google_page_content = self.get_page(vol_id, page_id, self.google_ocr)
            diffs = get_diffs(page.content, google_page_content)
        elif diff_with == PechaType.derge:
            derge_page_content = self.get_page(vol_id, page_id, self.derge)
            diffs = get_diffs(page.content, derge_page_content)
        else:
            old_page_content = self.get_page(vol_id, page_id)
            diffs = get_diffs(page.content, old_page_content)

        return diffs
