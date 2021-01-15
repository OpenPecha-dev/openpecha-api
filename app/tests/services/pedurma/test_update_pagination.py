import pytest
import yaml

from app.schemas.pecha import PedurmaNoteEdit
from app.services.pedurma.pagination_update import update_pagination


def from_yaml(yml_path):
    return yaml.safe_load(yml_path.read_text(encoding='utf-8'))

def to_yaml(dict_):
    return yaml.safe_dump(dict_, sort_keys = False, allow_unicode=True)

def test_pagination_update():
    text_id = "D1118"
    pecha_id = "P000792"
    layer_path = f"./tests/services/pedurma/data/Pagination.yml"
    pages_to_edit = {
        'v001': [
                    PedurmaNoteEdit(image_link = 'hei', image_no = 225, page_no= 187,ref_start_page_no= '178', ref_end_page_no = '180'),
                    PedurmaNoteEdit(image_link = 'hei', image_no = 226, page_no = 188,ref_start_page_no= '181', ref_end_page_no = '187'),
                ]
    }
        
    new_pagination_layer = to_yaml(update_pagination(pecha_id, text_id, pages_to_edit))
    expected_layer = from_yaml(Path(layer_path))
    assert new_pagination_layer == expected_layer
    
    