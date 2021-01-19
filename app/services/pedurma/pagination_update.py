import yaml
from pathlib import Path
from openpecha.cli import download_pecha

from app.schemas.pecha import PedurmaNoteEdit


def from_yaml(yml_path):
    return yaml.safe_load(yml_path.read_text(encoding='utf-8'))

def to_yaml(dict_):
    return yaml.safe_dump(dict_, sort_keys = False, allow_unicode=True)

def get_text_info(text_id, index):
    texts = index['annotations']
    for uuid, text in texts.items():
        if text['work_id'] == text_id:
            return (uuid, text)
    return ('', '')

def get_page_num(page_ann):
    pg_num = int(page_ann[:-1]) * 2
    pg_face = page_ann[-1]
    if pg_face == "a":
        pg_num -= 1
    return pg_num


def get_start_page(pagination, start):
    pages = pagination['annotations']
    for uuid, page in pages.items():
        if page['span']['end'] > start:
            return get_page_num(page['page_index'])
    return ''

def get_pg_index(pg_num):
    pg_idx = ''
    base_pg_num = int(pg_num / 2)
    if pg_num%2 == 0:
        pg_idx = f"{base_pg_num}b"
    else:
        pg_idx = f"{base_pg_num+1}a"
    return pg_idx


def get_pg_offset(first_pg_ref, span, pagination_layer):
    start = span['start']
    start_page = get_start_page(pagination_layer, start)
    return start_page-first_pg_ref

def update_pagination_annotation(durchen_pg_idx, pg_idx, paginations):
    for uuid, pagination in paginations.items():
        if pagination['page_index'] == pg_idx:
            paginations[uuid]['note_ref'] = durchen_pg_idx
            return paginations
    return paginations


def add_note_pg_ref(page_to_edit, pagination_layer):
    try:
        start_pg = int(page_to_edit.ref_start_page_no)
        end_pg = int(page_to_edit.ref_end_page_no)
    except:
        return pagination_layer
    durchen_image_num = page_to_edit.image_no
    offset = durchen_image_num - int(page_to_edit.page_no)
    durchen_pg_idx = get_pg_index(durchen_image_num)
    paginations = pagination_layer['annotations']
    if start_pg != 0 and end_pg != 0:
        for pg in range(start_pg, end_pg+1):
            pg_num = pg + offset
            pg_idx = get_pg_index(pg_num)
            paginations = update_pagination_annotation(durchen_pg_idx, pg_idx, paginations)
    pagination_layer['annotations'] = paginations
    return pagination_layer


def update_pg_ref(vol, pages_to_edit, pagination_layer):
    for page_to_edit in pages_to_edit:
        if vol == page_to_edit.vol:
            pagination_layer = add_note_pg_ref(page_to_edit, pagination_layer)
    return pagination_layer


def update_pagination(pecha_id, text_id, pedurma_edit_notes, opf_path):
    #opf_path = download_pecha(pecha_id)
    index = from_yaml(Path(f"{opf_path}/{pecha_id}.opf/index.yml"))
    text_uuid, text_info = get_text_info(text_id, index)
    for span in text_info['span']:
        vol = span['vol']
        pagination_layer = from_yaml(Path(f"{opf_path}/{pecha_id}.opf/layers/v{int(vol):03}/Pagination.yml"))
        pagination_layer = update_pg_ref(vol, pedurma_edit_notes, pagination_layer)
        yield vol, pagination_layer

    