from typing import Optional

from fastapi import APIRouter

from app import schemas

router = APIRouter()

pages = [
    schemas.pecha.Page(
        id="1", page_no="1", content="page 1 content", name="Page 1", notes_page_id="1"
    ),
    schemas.pecha.Page(
        id="2", page_no="2", content="page 2 content", name="Page 2", notes_page_id="1"
    ),
]

notes = [
    schemas.pecha.NotesPage(
        id="1", page_no="1", content="note 1 content", name="Page 100"
    )
]


@router.get("/{pecha_id}/texts/{text_id}", response_model=schemas.Text)
def get_text(pecha_id: str, text_id: str, page_no: Optional[int] = None):
    if page_no:
        return schemas.Text(id=text_id, pages=[pages[0]], notes=notes)
    return schemas.Text(id=text_id, pages=pages, notes=notes)
