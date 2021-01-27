from pathlib import Path

import pytest
import yaml

from app.schemas.pecha import NotesPage, Page, PageBase
from app.services.pedurma_reconstruction.reconstruction import get_preview_page


def from_yaml(yml_path):
    return yaml.safe_load(yml_path.read_text(encoding="utf-8"))


def test_get_preview_page():
    gb_pg_yml = from_yaml(
        Path("./app/tests/services/reconstruction/data/page_obj/109b_dg.yml")
    )
    g_body_page = Page(
        id=gb_pg_yml["id"],
        page_no=gb_pg_yml["page_no"],
        content=gb_pg_yml["content"],
        name=gb_pg_yml["name"],
        vol=gb_pg_yml["vol"],
        image_link=gb_pg_yml["image_link"],
        note_ref=gb_pg_yml["note_ref"],
    )
    nb_pg_yml = from_yaml(
        Path("./app/tests/services/reconstruction/data/page_obj/109b_n.yml")
    )
    n_body_page = Page(
        id=nb_pg_yml["id"],
        page_no=nb_pg_yml["page_no"],
        content=nb_pg_yml["content"],
        name=nb_pg_yml["name"],
        vol=nb_pg_yml["vol"],
        image_link=nb_pg_yml["image_link"],
        note_ref=nb_pg_yml["note_ref"],
    )
    gd_pg_yml = from_yaml(
        Path("./app/tests/services/reconstruction/data/notes_page_obj/113a_g.yml")
    )
    g_durchen_page = NotesPage(
        id=gd_pg_yml["id"],
        page_no=gd_pg_yml["page_no"],
        content=gd_pg_yml["content"],
        name=gd_pg_yml["name"],
        vol=gd_pg_yml["vol"],
        image_link=gd_pg_yml["image_link"],
    )
    nd_pg_yml = from_yaml(
        Path("./app/tests/services/reconstruction/data/notes_page_obj/113a_n.yml")
    )
    n_durchen_page = NotesPage(
        id=nd_pg_yml["id"],
        page_no=nd_pg_yml["page_no"],
        content=nd_pg_yml["content"],
        name=nd_pg_yml["name"],
        vol=nd_pg_yml["vol"],
        image_link=nd_pg_yml["image_link"],
    )
    expected_prev_page = Path(
        "./app/tests/services/reconstruction/data/prev_pg.txt"
    ).read_text(encoding="utf-8")
    preview_page = get_preview_page(
        g_body_page, n_body_page, g_durchen_page, n_durchen_page
    )
    assert expected_prev_page == preview_page
