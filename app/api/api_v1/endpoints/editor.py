from typing import List, Optional

from fastapi import APIRouter

from app import schemas
from app.services.pedurma.notes import get_pedurma_text_edit_notes
from app.services.pedurma.pagination_update import update_text_pagination
from app.services.pedurma_reconstruction.reconstruction import get_preview_page

router = APIRouter()


def get_text_pages_and_notes(name: str) -> schemas.Text:
    pages = [
        schemas.pecha.Page(
            id=str(i),
            page_no=str(i),
            content=f"{name} page {i} content",
            name=f"Page {i}",
            notes_page_id="1",
        )
        for i in range(1, 3)
    ]

    notes = [
        schemas.pecha.NotesPage(
            id="1", page_no="1", content="note 1 content", name="Page 100"
        ),
        schemas.pecha.NotesPage(
            id="2", page_no="2", content="note 2 content", name="Page 100"
        ),
    ]
    return pages, notes


@router.get("/{pecha_id}/texts/{text_id}", response_model=schemas.Text)
def get_text(pecha_id: str, text_id: str, page_no: Optional[int] = None):
    pages, notes = get_text_pages_and_notes(pecha_id)
    if page_no:
        return schemas.Text(id=text_id, pages=[pages[0]], notes=notes)
    return schemas.Text(id=text_id, pages=pages, notes=notes)


@router.post("/predurma/save")
def save_text(text: schemas.Text):
    return f"Text {text.id} saved!"


@router.post("/pedurma/preview", response_model=schemas.PedurmaPreviewPage)
def pedurma_page_preview(
    google_page: schemas.Page,
    google_page_note: schemas.NotesPage,
    namsel_page: schemas.Page,
    namsel_page_note: schemas.NotesPage,
):
    preview_page = get_preview_page(
        google_page, namsel_page, google_page_note, namsel_page_note
    )
    return preview_page


@router.get(
    "/pedurma/{text_id}/notes", response_model=List[schemas.pecha.PedurmaNoteEdit]
)
def get_text_notes(text_id: str):
    notes = get_pedurma_text_edit_notes(text_id)
    return notes


@router.post("/pedurma/{text_id}/notes")
def update_text_notes(text_id: str, notes: List[schemas.pecha.PedurmaNoteEdit]):
    update_text_pagination(text_id, notes)
