import re
from pathlib import Path
from typing import List, Optional

import yaml
from openpecha.cli import download_pecha
from openpecha.serializers import HFMLSerializer
from pydantic import BaseModel

from app.schemas.pecha import *


def from_yaml(yml_path):
    return yaml.safe_load(yml_path.read_text(encoding="utf-8"))


def get_text_info(text_id, index):
    texts = index["annotations"]
    for uuid, text in texts.items():
        if text["work_id"] == text_id:
            return (uuid, text)
    return ("", "")


def get_meta_data(pecha_id, text_uuid, meta_data):
    meta = {}

    meta = {
        "work_id": meta_data["work_id"],
        "img_grp_offset": meta_data["img_grp_offset"],
        "pref": meta_data["pref"],
        "pecha_id": pecha_id,
        "text_uuid": text_uuid,
    }
    return meta


def get_hfml_text(opf_path, text_id):
    serializer = HFMLSerializer(opf_path, text_id=text_id)
    serializer.apply_layers()
    hfml_text = serializer.get_result()
    return hfml_text


def add_first_page_ann(text):
    lines = text.splitlines()
    line_pat = re.search(r"\[(\w+)\.(\d+)\]", lines[1])
    page_ann = f"[{line_pat.group(1)}]"
    line_ann = f"[{line_pat.group(1)}.{int(line_pat.group(2))-1}]"
    new_text = f"{page_ann}\n{line_ann}{text}"
    return new_text


def get_body_text(text_with_durchen):
    try:
        durchen_starting = re.search("<[𰵀-󴉱]?d", text_with_durchen).start()
        text_content = text_with_durchen[:durchen_starting]
    except Exception:
        text_content = text_with_durchen
    return text_content


def get_durchen(text_with_durchen):
    durchen = ""
    try:
        durchen_start = re.search("<[𰵀-󴉱]?d", text_with_durchen).start()
        durchen_end = re.search("d>", text_with_durchen).end()
        durchen = text_with_durchen[durchen_start:durchen_end]
        durchen = add_first_page_ann(durchen)
    except Exception:
        print("durchen not found")
    return durchen


def get_pages(vol_text):
    result = []
    pg_text = ""
    pages = re.split(r"(\[[𰵀-󴉱]?[0-9]+[a-z]{1}\])", vol_text)
    for i, page in enumerate(pages[1:]):
        if i % 2 == 0:
            pg_text += page
        else:
            pg_text += page
            result.append(pg_text)
            pg_text = ""
    return result


def get_page_id(page_idx, pagination_layer):
    paginations = pagination_layer["annotations"]
    for uuid, pagination in paginations.items():
        if pagination["page_index"] == page_idx:
            return (uuid, pagination)
    return ("", "")


def get_page_num(page_ann):
    pg_num = int(page_ann[:-1]) * 2
    pg_face = page_ann[-1]
    if pg_face == "a":
        pg_num -= 1
    return pg_num


def get_link(pg_num, text_meta):
    vol = text_meta["vol"]
    img_group_offset = text_meta["img_grp_offset"]
    pref = text_meta["pref"]
    igroup = f"{pref}{img_group_offset+vol}"
    link = f"https://iiif.bdrc.io/bdr:{igroup}::{igroup}{int(pg_num):04}.jpg/full/max/0/default.jpg"
    return link


def get_note_ref(pagination):
    try:
        return pagination["note_ref"]
    except Exception:
        return ""


def get_clean_page(page):
    page_content = re.sub(r"\[([𰵀-󴉱])?[0-9]+[a-z]{1}\]", "", page)
    page_content = re.sub(r"\[(\w+)\.(\d+)\]", "", page_content)
    return page_content


def get_page_obj(page, text_meta, tag, pagination_layer):
    page_idx = re.search(r"\[([𰵀-󴉱])?([0-9]+[a-z]{1})\]", page).group(2)
    page_id, pagination = get_page_id(page_idx, pagination_layer)
    page_content = page
    pg_num = get_page_num(page_idx)
    page_link = get_link(pg_num, text_meta)
    note_ref = get_note_ref(pagination)
    if get_clean_page(page_content) == "\n":
        page_obj = None
    else:
        if tag == "note":
            page_obj = NotesPage(
                id=page_id,
                page_no=pg_num,
                content=page_content,
                name=f"Page {pg_num}",
                vol=text_meta["vol"],
                image_link=page_link,
            )
        else:
            page_obj = Page(
                id=page_id,
                page_no=pg_num,
                content=page_content,
                name=f"Page {pg_num}",
                vol=text_meta["vol"],
                image_link=page_link,
                note_ref=note_ref,
            )

    return page_obj


def get_page_obj_list(text, text_meta, pagination_layer, tag="text"):
    page_obj_list = []
    pages = get_pages(text)
    for page in pages:
        pg_obj = get_page_obj(page, text_meta, tag, pagination_layer)
        if pg_obj:
            page_obj_list.append(pg_obj)
    return page_obj_list


def construct_text_obj(hfmls, text_meta, opf_path):
    pages = []
    notes = []
    for vol_num, hfml_text in hfmls.items():
        text_meta["vol"] = int(vol_num[1:])
        pagination_layer = from_yaml(
            Path(
                f"{opf_path}/{text_meta['pecha_id']}.opf/layers/v{int(text_meta['vol']):03}/Pagination.yml"
            )
        )
        if not re.search(r"\[([𰵀-󴉱])?([0-9]+[a-z]{1})\]", hfml_text[:10]):
            hfml_text = add_first_page_ann(hfml_text)
        body_text = get_body_text(hfml_text)
        durchen = get_durchen(hfml_text)
        pages += get_page_obj_list(body_text, text_meta, pagination_layer, tag="text")
        if durchen:
            notes += get_page_obj_list(durchen, text_meta, pagination_layer, tag="note")
    text_obj = Text(id=text_meta["text_uuid"], pages=pages, notes=notes)
    return text_obj


def serialize_text_obj(text):
    text_hfml = ""
    pages = text.pages
    notes = text.notes
    for page in pages:
        text_hfml += page.content
    for note in notes:
        text_hfml += note.content
    return text_hfml


def get_text_obj(pecha_id, text_id):
    pecha_path = download_pecha(pecha_id)
    meta_data = from_yaml(Path(f"{pecha_path}/{pecha_id}.opf/meta.yml"))
    hfmls = get_hfml_text(f"{pecha_path}/{pecha_id}.opf/", text_id)
    index = from_yaml(Path(f"{pecha_path}/{pecha_id}.opf/index.yml"))
    text_uuid, text = get_text_info(text_id, index)
    text_meta = get_meta_data(pecha_id, text_uuid, meta_data)
    text = construct_text_obj(hfmls, text_meta, pecha_path)
    return text


# if __name__ == "__main__":
#     text_id = 'D1118'
#     pecha_id = 'P000792'
#     opf_path = f'./test/{pecha_id}.opf'
#     index = from_yaml(Path(f"./test/{pecha_id}.opf/index.yml"))
#     meta_data = from_yaml(Path(f"./test/{pecha_id}.opf/meta.yml"))
#     text_uuid, text_info = get_text_info(text_id, index)
#     text_meta = get_meta_data(pecha_id, text_uuid, meta_data)
#     hfmls = get_hfml_text(text_id, opf_path)
#     text_obj = get_text_obj(hfmls, text_meta, opf_path)
