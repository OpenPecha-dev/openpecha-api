import pytest
import yaml

from pathlib import Path
from app.schemas.pecha import PedurmaNoteEdit
from app.services.pedurma.pagination_update import update_pagination


def from_yaml(yml_path):
    return yaml.safe_load(yml_path.read_text(encoding='utf-8'))

def to_yaml(dict_):
    return yaml.safe_dump(dict_, sort_keys = False, allow_unicode=True)

def test_pagination_update_crossvol():
    text_id = "D1118"
    pecha_id = "P000002"
    layer_path = f"./app/tests/services/pedurma/data/Pagination.yml"
    opf_path = "./app/tests/services/pedurma/data/"
    pages_to_edit = [
                    PedurmaNoteEdit(image_link = 'https://iiif.bdrc.io/bdr:I1PD95846::I1PD958460004.jpg/full/max/0/default.jpg', image_no = 4, page_no= 4,ref_start_page_no= '1', ref_end_page_no = '3', vol = 1),
                    PedurmaNoteEdit(image_link = 'https://iiif.bdrc.io/bdr:I1PD95846::I1PD958460005.jpg/full/max/0/default.jpg', image_no = 5, page_no = 5,ref_start_page_no= '4', ref_end_page_no = '4', vol = 1),
                    PedurmaNoteEdit(image_link = 'https://iiif.bdrc.io/bdr:I1PD95847::I1PD958470004.jpg/full/max/0/default.jpg', image_no = 4, page_no= 4,ref_start_page_no= '1', ref_end_page_no = '3', vol = 2),
                    PedurmaNoteEdit(image_link = 'https://iiif.bdrc.io/bdr:I1PD95847::I1PD958470005.jpg/full/max/0/default.jpg', image_no = 5, page_no = 5,ref_start_page_no= '0', ref_end_page_no = '0', vol = 2),
                ]
    for vol, new_pagination_layer in update_pagination(pecha_id, text_id, pages_to_edit, opf_path):
        layer_path = f"./app/tests/services/pedurma/data/paginations/{text_id}/v{int(vol):03}.yml"
        expected_layer = from_yaml(Path(layer_path))
        assert new_pagination_layer == expected_layer

def test_pagination_update():
    text_id = "D1119"
    pecha_id = "P000002"
    layer_path = f"./app/tests/services/pedurma/data/Pagination.yml"
    opf_path = "./app/tests/services/pedurma/data/"
    pages_to_edit = [
                    PedurmaNoteEdit(image_link = 'https://iiif.bdrc.io/bdr:I1PD95847::I1PD958470004.jpg/full/max/0/default.jpg', image_no = 9, page_no= 9,ref_start_page_no= '7', ref_end_page_no = '8', vol = 2),
                    PedurmaNoteEdit(image_link = 'https://iiif.bdrc.io/bdr:I1PD95847::I1PD958470005.jpg/full/max/0/default.jpg', image_no = 10, page_no = 10,ref_start_page_no= '0', ref_end_page_no = '0', vol = 2),
                ]
    for vol, new_pagination_layer in update_pagination(pecha_id, text_id, pages_to_edit, opf_path):
        layer_path = f"./app/tests/services/pedurma/data/paginations/{text_id}/v{int(vol):03}.yml"
        expected_layer = from_yaml(Path(layer_path))
        assert new_pagination_layer == expected_layer
    
    