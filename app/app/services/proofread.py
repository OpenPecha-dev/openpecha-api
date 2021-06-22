import re
from pathlib import Path
from typing import List, Tuple

from openpecha.config import BASE_PATH
from openpecha.core.layer import LayerEnum
from openpecha.core.pecha import OpenPechaFS
from openpecha.serializers import HFMLSerializer

from .pechas import get_pecha


def ensure_path_exists(path: Path):
    if not path.is_dir():
        path.mkdir(exist_ok=True, parents=True)
    return path


class Proofread:
    """
    Proofread class prepare and serve pages to be proof read.

    Args:
        transk (str): transkribus pecha id
        google_ocr (str): google ocred pecha id
        derge (str): derge pecha id
    """

    def __init__(self, transk, google_ocr, derge):
        self.transkribus = transk
        self.google_ocr = google_ocr
        self.derge = derge
        self.base_path = BASE_PATH / "proofread"
        self.__prepare_data()

    def __apply_pagination_layer(self, pecha: OpenPechaFS):
        pagination = LayerEnum("Pagination").value
        serializers = HFMLSerializer(
            pecha.opf_path,
            vol_ids=["v048"],  # "v049", "v050", "v051", "v052", "v053"],
            layers=[pagination],
        )
        # for vol_id in pecha.components:
        serializers.apply_layer("v048", pagination)
        # break
        result = serializers.get_result()
        return result

    def __get_pages_content(self, text: str):
        pages_content = re.split(r"\[.*", text)[1:]
        striped_pages_content = map(lambda line: line.strip(), pages_content)
        return striped_pages_content

    def __find_page_name(self, page_info: str):
        match = re.search("\[.*\] (.*)", page_info)
        page_name = match.group(1)
        return page_name.replace("_", "")

    def __get_pages_name(self, text: str):
        pages_info = re.findall("\[.*", text)
        return map(self.__find_page_name, pages_info)

    def __split_into_pages(self, text: str) -> List[Tuple[str, str]]:
        pages_content = self.__get_pages_content(text)
        pages_name = self.__get_pages_name(text)
        return zip(pages_name, pages_content)

    def __save_pages(self, pecha_id, vol_id, page) -> None:
        vol_dir = ensure_path_exists(self.base_path / pecha_id / f"{vol_id}")
        page_name, page_content = page
        page_fn = vol_dir / f"{page_name}.txt"
        page_fn.write_text(page_content)

    def __process_pecha(self, pecha: OpenPechaFS):
        pecha_page_view = self.__apply_pagination_layer(pecha)
        for vol_id, vol_page_view in pecha_page_view.items():
            for page in self.__split_into_pages(vol_page_view):
                self.__save_pages(pecha.pecha_id, vol_id, page)

    def __prepare_data(self):
        transkribus_pecha = get_pecha(self.transkribus, branch="master")
        self.__process_pecha(transkribus_pecha)

        google_orc_pecha = get_pecha(self.google_orc, branch="master")
        self.__process_pecha(google_orc_pecha)

        derge_pecha = get_pecha(self.derge, branch="master")
