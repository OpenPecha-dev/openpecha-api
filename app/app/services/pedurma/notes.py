import re
from pathlib import Path

import yaml
from openpecha.cli import download_pecha
from openpecha.serializers import HFMLSerializer

from app.schemas.pecha import PedurmaNoteEdit


def from_yaml(yml_path):
    return yaml.safe_load(yml_path.read_text(encoding="utf-8"))


def get_meta_data(text_uuid, meta_data):
    try:
        meta = {
            "work_id": meta_data["work_id"],
            "img_grp_offset": meta_data["img_grp_offset"],
            "pref": meta_data["pref"],
            "text_uuid": text_uuid,
        }
    except Exception:
        meta = {}
    return meta


def add_first_page_ann(text):
    lines = text.splitlines()
    line_pat = re.search(r"\[(\w+)\.(\d+)\]", lines[1])
    page_ann = f"[{line_pat.group(1)}]"
    line_ann = f"[{line_pat.group(1)}.{int(line_pat.group(2))-1}]"
    new_text = f"{page_ann}\n{line_ann}{text}"
    return new_text


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


def get_durchen_pages(vol_text):
    durchen_pages = {}
    pages = re.split(r"(\[[𰵀-󴉱]?[0-9]+[a-z]{1}\])", vol_text)
    pg_ann = ""
    for i, page in enumerate(pages[1:]):
        if i % 2 == 0:
            pg_ann = page
        else:
            durchen_pages[pg_ann] = page
    return durchen_pages


def get_page_num(page_ann):
    pg_pat = re.search(r"(\d+[a-z]{1})", page_ann)
    pg_num = int(pg_pat.group(1)[:-1]) * 2
    pg_face = pg_pat.group(1)[-1]
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


def rm_annotations(text, annotations):
    clean_text = text
    for ann in annotations:
        clean_text = re.sub(ann, "", clean_text)
    return clean_text


def preprocess_namsel_notes(text):
    """
    this cleans up all note markers
    :param text: plain text
    :return: cleaned text
    """

    patterns = [
        # normalize single zeros '༥༥་' --> '༥༥༠'
        [r"([༠-༩])[་༷]", r"\g<1>༠"],
        # normalize double zeros '༧༷་' --> '༧༠༠'
        [r"༠[་༷]", r"༠༠"],
        [r"༠[་༷]", r"༠༠"],
        # normalize punct
        [r"\r", r"\n"],
        [r"༑", r"།"],
        [r"།།", r"། །"],
        [r"།་", r"། "],
        [r"\s+", r" "],
        [r"།\s།\s*\n", r"།\n"],
        [r"།\s།\s«", r"། «"],
        [r"༌", r"་"],  # normalize NB tsek
        [r"ག\s*།", r"ག"],
        [r"་\s*", r"་"],
        [r"་\s*", r"་"],
        [r"་\s*\n", r"་"],
        [r"་+", r"་"],
        # normalize and tag page numbers '73ཝ་768' --> ' <p73-768> '
        [r"([0-9]+?)[ཝ—-]་?([0-9]+)", r" <p\g<1>-\g<2>> "],
        # tag page references '༡༤༥ ①' --> <p༡༤༥> ①'
        [r" ?([༠-༩]+?)(\s\(?[①-⓪༠-༩ ཿ༅]\)?)", r" \n<r\g<1>>\g<2>"],  # basic page ref
        # normalize edition marks «<edition>»
        [r"〈〈?", r"«"],
        [r"〉〉?", r"»"],
        [r"《", r"«"],
        [r"》", r"»"],
        [r"([ཀགཤ།]) །«", r"\g<1> «"],
        [r"([ཀགཤ།])་?«", r"\g<1> «"],
        [r"»\s+", r"»"],
        [r"«\s+«", r"«"],
        [r"»+", r"»"],
        [r"[=—]", r"-"],
        [r"\s+-", r"-"],
        [r"\s+\+", r"+"],
        [r"»\s+«", r"»«"],
    ]

    for p in patterns:
        text = re.sub(p[0], p[1], text)

    return text


def get_num(line):
    tib_num = re.sub(r"\W", "", line)
    tib_num = re.sub(r"(\d+?)r", "", tib_num)
    table = tib_num.maketrans("༡༢༣༤༥༦༧༨༩༠", "1234567890", "<r>")
    eng_num = int(tib_num.translate(table))
    return eng_num


def get_durchen_pg_num(clean_page):
    pg_num = 0
    try:
        page_ann = re.findall(r"<p\d+-(\d+)\>", clean_page)
        pg_num = page_ann[-1]
    except Exception:
        pass
    return pg_num


def get_page_refs(page_content):
    refs = re.findall(r"<r.+?>", page_content)
    if refs:
        if len(refs) > 2:
            refs[0] = get_num(refs[0])
            refs[-1] = get_num(refs[-1])
            return (refs[0], refs[-1])
        else:
            refs[0] = get_num(refs[0])
            return (refs[0], "0")
    else:
        return ("0", "0")


def process_page(page_ann, page_content, text_meta):
    durchen_image_num = get_page_num(page_ann)
    pg_link = get_link(durchen_image_num, text_meta)
    unwanted_annotations = [
        r"\[([𰵀-󴉱])?[0-9]+[a-z]{1}\]",
        r"\[\w+\.\d+\]",
        r"<d",
        r"d>",
    ]
    page_content = rm_annotations(page_content, unwanted_annotations)
    clean_page = preprocess_namsel_notes(page_content)
    durchen_pg_num = get_durchen_pg_num(clean_page)
    pg_ref_first, pg_ref_last = get_page_refs(clean_page)
    page_obj = PedurmaNoteEdit(
        image_link=pg_link,
        image_no=durchen_image_num,
        page_no=durchen_pg_num,
        ref_start_page_no=pg_ref_first,
        ref_end_page_no=pg_ref_last,
        vol=text_meta["vol"],
    )
    return page_obj


def get_pages_to_edit(durchen_pages, text_meta):
    pages_to_edit = []
    for page_ann, page_content in durchen_pages.items():
        pages_to_edit.append(process_page(page_ann, page_content, text_meta))
    return pages_to_edit


def get_hfml_text(opf_path, text_id):
    serializer = HFMLSerializer(f"{opf_path}/P000792.opf", text_id=text_id)
    serializer.apply_layers()
    hfml_text = serializer.get_result()
    return hfml_text


def get_pedurma_edit_notes(hfml_text, text_meta):
    pedurma_edit_notes = []
    for vol, text_content in hfml_text.items():
        text_meta["vol"] = int(vol[1:])
        durchen = get_durchen(text_content)
        durchen_pages = get_durchen_pages(durchen)
        pedurma_edit_notes += get_pages_to_edit(durchen_pages, text_meta)
    return pedurma_edit_notes


def get_pedurma_text_edit_notes(text_id):
    pecha_path = download_pecha("P000792", needs_update=False)
    meta_data = from_yaml(Path(f"{pecha_path}/P000792.opf/meta.yml"))
    hfmls = get_hfml_text(pecha_path, text_id)
    pedurma_edit_notes = get_pedurma_edit_notes(hfmls, meta_data)
    return pedurma_edit_notes
