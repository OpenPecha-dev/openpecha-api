import json
from enum import Enum
from pathlib import Path
from typing import Dict, List

from antx.core import get_diffs
from openpecha.config import BASE_PATH

from app.schemas.proofread import ProofreadPage

from .diff import Diff


def path2names(paths):
    return [path.stem for path in paths]


def list_sorted_paths_name(path):
    return path2names(sorted((path.iterdir())))


class PechaType(str, Enum):
    transk = "transk"
    google_ocr = "google_ocr"
    derge = "derge"


class Metadata:
    """
    {
        "v001": {
            "pages": {
                "0001": {
                    "revision": 1,
                    "image_url": https://...,
                    "offset": 10
                },
            },
            "imagegroup": "I1KG14011"
        }
    }
    """

    def __init__(self, base_path: Path, transk: str):
        self.transkribus = transk
        self.base_path: Path = base_path
        self.metadata_fn: Path = self.base_path / "metadata.json"
        self._metadata: Dict = None

    def __load_metadata(self) -> None:
        if self._metadata:
            return
        self._metadata = json.load(self.metadata_fn.open())

    def __save_metadata(self) -> None:
        json.dump(self._metadata, self.metadata_fn.open("w"))

    def get_vols(self) -> List[str]:
        if not self.metadata_fn.is_file():
            vols = list_sorted_paths_name(self.base_path / self.transkribus)
            self._metadata = {vol: {} for vol in vols}
            self.__save_metadata()

        if not self._metadata:
            self.__load_metadata()

        return list(self._metadata.keys())

    def get_pages(self, vol_id: str) -> List[str]:
        if not self.metadata_fn.is_file():
            self.get_vols()

        if not self._metadata:
            self.__load_metadata()

        if not self._metadata[vol_id]:
            pages = list_sorted_paths_name(self.base_path / self.transkribus / vol_id)
            self._metadata[vol_id]["pages"] = {page: {} for page in pages}
            self.__save_metadata()

        return self._metadata[vol_id]["pages"]

    def __increment_page_revision(self, page) -> int:
        if "revision" not in page:
            return 1
        return page["revision"] + 1

    def __create_page(self, image_url, offset):
        return {"revision": 0, "image_url": image_url, "offset": offset}

    def save_page(self, vol_id: str, page_id: str, image_url: str, offset=None):
        self.__load_metadata()
        if (
            page_id not in self._metadata[vol_id]["pages"]
            or not self._metadata[vol_id]["pages"][page_id]
        ):
            self._metadata[vol_id]["pages"][page_id] = self.__create_page(
                image_url, offset
            )
            self.__save_metadata()
            return

        page = self._metadata[vol_id]["pages"][page_id]
        page["revision"] = self.__increment_page_revision(page)
        page["image_url"] = image_url
        page["offset"] = offset
        self.__save_metadata()

    @staticmethod
    def __int2page_id(n: int) -> str:
        return f"{n:04}"

    def __get_previous_offset(self, vol_id: str, page_id: str) -> int:
        prev_page = {}
        prev_page_id = page_id
        while "offset" not in prev_page:
            prev_page_id = self.__int2page_id(int(prev_page_id) - 1)
            if prev_page_id == "0000":
                return 0
            prev_page = self._metadata[vol_id]["pages"][prev_page_id]
        return prev_page["offset"]

    def get_offset(self, vol_id: str, page_id: str) -> int:
        self.__load_metadata()
        if "offset" not in self._metadata[vol_id]["pages"][page_id]:
            return self.__get_previous_offset(vol_id, page_id)

        return self._metadata[vol_id]["pages"][page_id]["offset"]


class ImageManager:
    """
    Issue correct image to the specific page text
    """

    def __init__(self, base_path, metadata: Metadata):
        self.metadata = metadata
        self.vol2imagegroup_fn = base_path / "vol2imagegroup.json"
        self._vol2imagegroup = None
        self.image_url_format = (
            "https://iiif.bdrc.io/bdr:{imagegroup}::{filename}/full/max/0/default.jpg"
        )

    @property
    def vol2imagegroup(self):
        if self._vol2imagegroup:
            return self._vol2imagegroup
        return json.load(self.vol2imagegroup_fn.open())

    def __get_image_order(self, vol_id: str, page_id: str):
        return int(page_id) + self.metadata.get_offset(vol_id, page_id)

    def get_image_url(self, vol_id: str, page_id: str):
        imagegroup = self.vol2imagegroup[vol_id]
        filename = f"{imagegroup}{self.__get_image_order(vol_id, page_id):04}.jpg"
        return self.image_url_format.format(imagegroup=imagegroup, filename=filename)

    def get_offset(self, vol_id: str, page_id: str, image_url: str):
        _, filename = self.__parse_image_url(image_url)
        _, image_order, _ = self.__parse_filename(filename)
        return image_order - int(page_id)

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


class Proofread:
    """
    Proofread class prepare and serve pages to be proof read.

    Args:
        transk (str): transkribus pecha id
        google_ocr (str): google ocred pecha id
        derge (str): derge pecha id
    """

    def __init__(self, project_name: str, transk: str, google_ocr: str, derge: str):
        self.project_name = project_name
        self.transkribus = transk
        self.google_ocr = google_ocr
        self.derge = derge
        self.base_path: Path = BASE_PATH / "proofread" / self.project_name
        self.metadata = Metadata(self.base_path, self.transkribus)
        self.image_manager = ImageManager(self.base_path, self.metadata)

    def get_vols_metadata(self) -> List[str]:
        return self.metadata.get_vols()

    def get_pages_metadata(self, vol_id: str) -> List[str]:
        return self.metadata.get_pages(vol_id)

    def get_page(self, vol_id: str, page_id: str, pecha_id: str = None) -> str:
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
        offset = self.image_manager.get_offset(vol_id, page_id, page.image_url)
        self.metadata.save_page(vol_id, page_id, page.image_url, offset=offset)

    def get_image_url(self, vol_id: str, page_id: str) -> str:
        image_url = self.image_manager.get_image_url(vol_id, page_id)
        return image_url

    def get_diffs(
        self, vol_id: str, page_id: str, page: ProofreadPage, diff_with: PechaType
    ):
        if diff_with == PechaType.google_ocr:
            google_page_content = self.get_page(vol_id, page_id, self.google_ocr)
            diff = Diff(page.content, google_page_content)
        elif diff_with == PechaType.derge:
            derge_page_content = self.get_page(vol_id, page_id, self.derge)
            diff = Diff(page.content, derge_page_content)
        else:
            old_page_content = self.get_page(vol_id, page_id)
            diff = Diff(page.content, old_page_content)

        return diff.compute()
