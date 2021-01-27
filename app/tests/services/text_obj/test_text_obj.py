from pathlib import Path

import pytest
import yaml

from app.schemas.pecha import *
from app.services.text_obj.texts import *


def test_text_obj_serializer_corssvol():
    text_id = "D1118"
    pecha_id = "P000002"
    opf_path = f"./app/tests/services/text_obj/data/{pecha_id}/"
    index = from_yaml(Path(f"{opf_path}/{pecha_id}.opf/index.yml"))
    meta_data = {"work_id": "W1PD95844", "img_grp_offset": 845, "pref": "I1PD95"}
    text_uuid, text_info = get_text_info(text_id, index)
    text_meta = get_meta_data(pecha_id, text_uuid, meta_data)
    hfmls = from_yaml(Path(f"./app/tests/services/text_obj/data/hfmls/{text_id}.yml"))
    text_obj = construct_text_obj(hfmls, text_meta, opf_path)
    expected_text_obj = Text(
        id="259260e8e3544fc1a9a27d7dffc72df6",
        pages=[
            Page(
                id="1a26fd08bf2b4ebb9e2d7369347e478b",
                page_no=1,
                content="[\U00030d401a]\n[1a.1]{D1118}ཉ༄ཚོ། །རྒྱ་གར་སྐད་དུ།\n[1a.2]སྟ་བ་ནཱ་མ། བོད་སྐད་དུ།\n[1a.3]པར་འོས་པ་བསྔགས་\n",
                name="Page 1",
                vol="1",
                image_link="https://iiif.bdrc.io/bdr:I1PD95846::I1PD958460001.jpg/full/max/0/default.jpg",
                note_ref="46d97ed3d9ca4ddabc3c413f306df03a",
            ),
            Page(
                id="e8e314a7457b40348b5dd7a744004900",
                page_no=2,
                content="[\U00030d411b]\n[1b.1]གཏམ་འདི་ཙམ\n[1b.2]འདི་ཉིད་སྨྲ་བར་\n[1b.3]དང་-། །ཁྱོད་མ\n",
                name="Page 2",
                vol="1",
                image_link="https://iiif.bdrc.io/bdr:I1PD95846::I1PD958460002.jpg/full/max/0/default.jpg",
                note_ref="46d97ed3d9ca4ddabc3c413f306df03a",
            ),
            Page(
                id="29c64dc1fa624b42b08814ca4f3a78b4",
                page_no=3,
                content="[\U00030d422a]\n[2a.1]འདོད་གང་དག་\n[2a.2]སྐྱབས་འགྲོ་བ།\n[2a.3]སྟོང་གིས་ཀྱང་།\n",
                name="Page 3",
                vol="1",
                image_link="https://iiif.bdrc.io/bdr:I1PD95846::I1PD958460003.jpg/full/max/0/default.jpg",
                note_ref="46d97ed3d9ca4ddabc3c413f306df03a",
            ),
            Page(
                id="c11d8db649854c5d89ca3df22047d07b",
                page_no=1,
                content="[\U00030d401a]\n[1a.1]་་༄ལོ། །རྒྱ་གར་སྐད་དུ།\n[1a.2]དབྱིངས་སུ་བསྟོད་པ།\n[1a.3]འཚལ་ལོ། །གང་ཞིག་\n",
                name="Page 1",
                vol="2",
                image_link="https://iiif.bdrc.io/bdr:I1PD95847::I1PD958470001.jpg/full/max/0/default.jpg",
                note_ref="05d117045b0c4ea5aee3aeba558e94bd",
            ),
            Page(
                id="21671cb910d9486c8ba4793305c00d58",
                page_no=2,
                content="[\U00030d411b]\n[1b.1]མཐོང་ངོ་། །ཕྱོགས་\n[1b.2]དེ་དང་དེ་ཡི་ཕྱོགས་\n[1b.3]ཏིང་འཛིན་རྡོ་རྗེ་ཡིས\n",
                name="Page 2",
                vol="2",
                image_link="https://iiif.bdrc.io/bdr:I1PD95847::I1PD958470002.jpg/full/max/0/default.jpg",
                note_ref="05d117045b0c4ea5aee3aeba558e94bd",
            ),
            Page(
                id="671dc26715434318b3d641521d4e9292",
                page_no=3,
                content="[\U00030d422a]\n[2a.1]རིམ་གྱིས་སྦྱངས་\n[2a.2]མེད་ཉི་མ་ཟླ་བ་ཡང་།\n[2a.3]་རྡུལ་ལ་སོགས།\n",
                name="Page 3",
                vol="2",
                image_link="https://iiif.bdrc.io/bdr:I1PD95847::I1PD958470003.jpg/full/max/0/default.jpg",
                note_ref="05d117045b0c4ea5aee3aeba558e94bd",
            ),
        ],
        notes=[
            NotesPage(
                id="46d97ed3d9ca4ddabc3c413f306df03a",
                page_no=4,
                content="[2b]\n[2b.1]<\U00030d40dརྒྱ་གར་གྱི་\n[2b.2]༢༦༤ ༧པེ་〉〉་\n[2b.3]བཞུགས་གོ།d>",
                name="Page 4",
                vol="1",
                image_link="https://iiif.bdrc.io/bdr:I1PD95846::I1PD958460004.jpg/full/max/0/default.jpg",
            ),
            NotesPage(
                id="05d117045b0c4ea5aee3aeba558e94bd",
                page_no=4,
                content="[2b]\n[2b.1]<\U00030d40dའབྱོར་ཆེན་པོ་དེར་\n[2b.2]སྡུག་བསྔལ་གྱིས་\n[2b.3]དེ་ཡི་སྐུ་ལས་d>",
                name="Page 4",
                vol="2",
                image_link="https://iiif.bdrc.io/bdr:I1PD95847::I1PD958470004.jpg/full/max/0/default.jpg",
            ),
        ],
    )
    assert text_obj == expected_text_obj


def test_text_obj_serializer():
    text_id = "D1119"
    pecha_id = "P000002"
    opf_path = f"./app/tests/services/text_obj/data/{pecha_id}/"
    index = from_yaml(Path(f"{opf_path}/{pecha_id}.opf/index.yml"))
    meta_data = {"work_id": "W1PD95844", "img_grp_offset": 845, "pref": "I1PD95"}
    text_uuid, text_info = get_text_info(text_id, index)
    text_meta = get_meta_data(pecha_id, text_uuid, meta_data)
    hfmls = from_yaml(Path(f"./app/tests/services/text_obj/data/hfmls/{text_id}.yml"))
    text_obj = construct_text_obj(hfmls, text_meta, opf_path)
    expected_text_obj = Text(
        id="cf52cbae1a7640b688b24135fe566920",
        pages=[
            Page(
                id="3373e79434004aaeb8b2e69649243d2a",
                page_no=5,
                content="[\U00030d443a]\n[3a.1]{D1119}ངོས་ལྗོན་ཤིང་\n[3a.2]ལེན་པ་པོ་ཕུན་སུམ་ཚོགས་པའོ།\n[3a.3]འདི་དག་གིས་ནི་སྦྱིན་པར་\n",
                name="Page 5",
                vol="2",
                image_link="https://iiif.bdrc.io/bdr:I1PD95847::I1PD958470005.jpg/full/max/0/default.jpg",
                note_ref="9efa117a2b9444ac8cb09c198d21cdd8",
            ),
            Page(
                id="71dff610d4c841c58e9c815582bf8508",
                page_no=6,
                content="[\U00030d453b]\n[3b.1]མངའ་དབང་མཛད་པ་\n[3b.2]འདི་དག་གིས་ནི་དེའི་\n[3b.3]གིས་ནི་སྐྱེ་བ་ལ་\n",
                name="Page 6",
                vol="2",
                image_link="https://iiif.bdrc.io/bdr:I1PD95847::I1PD958470006.jpg/full/max/0/default.jpg",
                note_ref="9efa117a2b9444ac8cb09c198d21cdd8",
            ),
        ],
        notes=[
            NotesPage(
                id="9efa117a2b9444ac8cb09c198d21cdd8",
                page_no=7,
                content="[4a]\n[4a.1]<\U00030d41dདེ་ལ་ནམ་མཁའི་\n[4a.2]བ་ཡང་དག་པར་\n[4a.3]གིས་ནི་ཆོས་སྟོན་པའི་d>",
                name="Page 7",
                vol="2",
                image_link="https://iiif.bdrc.io/bdr:I1PD95847::I1PD958470007.jpg/full/max/0/default.jpg",
            )
        ],
    )
    assert text_obj == expected_text_obj
