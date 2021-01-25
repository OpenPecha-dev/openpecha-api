from pathlib import Path

import pytest

from app.schemas.pecha import NotesPage, Page
from app.services.pedurma_reconstruction.reconstruction import get_preview_page


def test_get_preview_page():
    g_body_page = Path(
        "./app/tests/services/reconstruction/data/109b_dg.txt"
    ).read_text(encoding="utf-8")
    n_body_page = Path("./app/tests/services/reconstruction/data/109b_n.txt").read_text(
        encoding="utf-8"
    )
    g_durchen_page = Path(
        "./app/tests/services/reconstruction/data/113a_g.txt"
    ).read_text(encoding="utf-8")
    n_durchen_page = Path(
        "./app/tests/services/reconstruction/data/113a_n.txt"
    ).read_text(encoding="utf-8")
    expected_prev_page = Path(
        "./app/tests/services/reconstruction/data/prev_pg.txt"
    ).read_text(encoding="utf-8")
    preview_page = get_preview_page(
        g_body_page, n_body_page, g_durchen_page, n_durchen_page
    )
    assert expected_prev_page == preview_page
