import pytest
import yaml

from app.schemas.pecha import PedurmaNoteEdit
from app.services.pedurma.pagination_update import update_pagination


def test_pagination_update():
    text_id = "D1118"
    opf_path = f"./tests/services/pedurma/data/"
    pages_to_edit = [
        PedurmaNoteEdit(image_link = 'hei', image_no = 225, page_no= 187,ref_start_page_no= '178', ref_end_page_no = '180'),
        PedurmaNoteEdit(image_link = 'hei', image_no = 226, page_no = 188,ref_start_page_no= '181', ref_end_page_no = '187'),
        ]
    
    