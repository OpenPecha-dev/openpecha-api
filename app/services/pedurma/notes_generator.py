import re 
import yaml
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel
from openpecha.serializers import HFMLSerializer

from app.schemas.pecha import PedurmaNoteEdit


def from_yaml(yml_path):
    return yaml.safe_load(yml_path.read_text(encoding='utf-8'))

def get_meta_data(pecha_id, text_uuid, meta_data):
    try:
        meta = {
            'work_id': meta_data['work_id'],
            'img_grp_offset': meta_data['img_grp_offset'],
            'pref': meta_data['pref'],
            'pecha_id': pecha_id,
            'text_uuid': text_uuid,
        }
    except:
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
    durchen = ''
    try:
        durchen_start = re.search("<d", text_with_durchen).start()
        durchen_end = re.search("d>", text_with_durchen).end()
        durchen = text_with_durchen[durchen_start:durchen_end]
        durchen = add_first_page_ann(durchen)
    except:
        print('durchen not found')
    return durchen


def get_durchen_pages(vol_text):
    durchen_pages = {}
    pg_text = ""
    pages = re.split(r"(\[[𰵀-󴉱]?[0-9]+[a-z]{1}\])", vol_text)
    for i, page in enumerate(pages[1:]):
        if i % 2 == 0:
            pg_ann = page
        else:
            durchen_pages[pg_ann]= page
    return durchen_pages



def get_page_num(page_ann):
    pg_pat = re.search('(\d+[a-z]{1})', page_ann)
    pg_num = int(pg_pat.group(1)[:-1]) * 2
    pg_face = pg_pat.group(1)[-1]
    if pg_face == "a":
        pg_num -= 1
    return pg_num 

def get_link(pg_num, text_meta):
    vol = text_meta["vol"]
    work = text_meta["work_id"]
    img_group_offset = text_meta["img_grp_offset"]
    pref = text_meta["pref"]
    igroup = f"{pref}{img_group_offset+vol}"
    link = f"https://iiif.bdrc.io/bdr:{igroup}::{igroup}{int(pg_num):04}.jpg/full/max/0/default.jpg"
    return link

def rm_annotations(text, annotations):
    clean_text = text
    for ann in annotations:
        clean_text = re.sub(ann, '', clean_text)
    return clean_text

def preprocess_namsel_notes(text):
    """
    this cleans up all note markers
    :param text: plain text
    :return: cleaned text
    """

    patterns = [
        # normalize single zeros '༥༥་' --> '༥༥༠'
        ["([༠-༩])[་༷]", "\g<1>༠"],
        # normalize double zeros '༧༷་' --> '༧༠༠'
        ["༠[་༷]", "༠༠"],
        ["༠[་༷]", "༠༠"],
        # normalize punct
        ["\r", "\n"],
        ["༑", "།"],
        ["།།", "། །"],
        ["།་", "། "],
        ["\s+", " "],
        ["།\s།\s*\n", "།\n"],
        ["།\s།\s«", "། «"],
        ["༌", "་"],  # normalize NB tsek
        ["ག\s*།", "ག"],
        ["་\s*", "་"],
        ["་\s*", "་"],
        ["་\s*\n", "་"],
        ["་+", "་"],
        # normalize and tag page numbers '73ཝ་768' --> ' <p73-768> '
        ["([0-9]+?)[ཝ—-]་?([0-9]+)", " <p\g<1>-\g<2>> "],
        # tag page references '༡༤༥ ①' --> <p༡༤༥> ①'
        [" ?([༠-༩]+?)(\s\(?[①-⓪༠-༩ ཿ༅]\)?)", " \n<r\g<1>>\g<2>"],  # basic page ref
        # normalize edition marks «<edition>»
        ["〈〈?", "«"],
        ["〉〉?", "»"],
        ["《", "«"],
        ["》", "»"],
        ["([ཀགཤ།]) །«", "\g<1> «"],
        ["([ཀགཤ།])་?«", "\g<1> «"],
        ["»\s+", "»"],
        ["«\s+«", "«"],
        ["»+", "»"],
        ["[=—]", "-"],
        ["\s+-", "-"],
        ["\s+\+", "+"],
        ["»\s+«", "»«"],  
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
    pg_num = ''
    try:
        page_ann = re.search('<p\d+-(\d+)\>', clean_page)
        pg_num= page_ann.group(1)
    except:
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
            return (refs[0], '')
    else:
        return ('', '')


def process_page(page_ann, page_content):
    durchen_image_num = get_page_num(page_ann)
    pg_link = get_link(durchen_image_num, text_meta)
    unwanted_annotations = ['\[([𰵀-󴉱])?[0-9]+[a-z]{1}\]', '\[\w+\.\d+\]', '<d', 'd>']
    page_content = rm_annotations(page_content, unwanted_annotations)
    clean_page = preprocess_namsel_notes(page_content)
    durchen_pg_num = get_durchen_pg_num(clean_page)
    pg_ref_first, pg_ref_last = get_page_refs(clean_page)
    page_obj = PedurmaNoteEdit(
        image_link=pg_link, image_no = durchen_image_num, page_no = durchen_pg_num,
        ref_start_page_no= pg_ref_first, ref_end_page_no = pg_ref_last
        )
    return page_obj


def get_pages_to_edit(durchen_pages, text_meta):
    pages_to_edit = []
    for page_ann, page_content in durchen_pages.items():
        pages_to_edit.append(process_page(page_ann, page_content))
    return pages_to_edit

def get_pedurma_edit_notes(pecha_id, text_id):
    pedurma_edit_notes = []
    opf_path = f"./test/{pecha_id}.opf/"
    meta_data = from_yaml(Path(f"./test/{pecha_id}.opf/meta.yml"))
    serializer = HFMLSerializer(opf_path, text_id=text_id)
    serializer.apply_layers()
    hfml_text  = serializer.get_result()
    text_meta = get_meta_data(pecha_id, text_id, meta_data)
    for vol, text_content in hfml_text.items():
        durchen_pages = {}
        text_meta['vol'] = int(vol[1:])
        durchen = get_durchen(text_content)
        durchen_pages = get_durchen_pages(durchen)
        pedurma_edit_notes += get_pages_to_edit(durchen_pages, text_meta)
    return pedurma_edit_notes
    
    


