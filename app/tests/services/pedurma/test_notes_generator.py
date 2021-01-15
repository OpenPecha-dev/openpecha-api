import pytest
import yaml

from app.schemas.pecha import PedurmaNoteEdit
from app.services.pedurma.notes_generator import get_pedurma_edit_notes


def test_notes_generator():
    pecah_id = "P000792"
    text_id = "D1118"
    result = get_pedurma_edit_notes(pecha_id, text_id)
    expected_result = {
        'v001': [
                    PedurmaNoteEdit(image_link = 'https://iiif.bdrc.io/bdr:I1PD95846::I1PD958460225.jpg/full/max/0/default.jpg', image_no = 225, page_no= 187,ref_start_page_no= '180', ref_end_page_no = ''),
                    PedurmaNoteEdit(image_link = 'https://iiif.bdrc.io/bdr:I1PD95846::I1PD958460226.jpg/full/max/0/default.jpg', image_no = 226, page_no = 188,ref_start_page_no= '1', ref_end_page_no = '2'),
                    PedurmaNoteEdit(image_link = 'https://iiif.bdrc.io/bdr:I1PD95846::I1PD958460227.jpg/full/max/0/default.jpg', image_no = 227, page_no = 0,ref_start_page_no= '', ref_end_page_no = ''),
                ]
    }
        
    assert result == expected_result
    
