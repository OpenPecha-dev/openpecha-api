from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, status

from app import schemas
from app.services.pedurma.notes import get_pedurma_text_edit_notes
from app.services.pedurma.pagination_update import update_text_pagination
from app.services.pedurma.text import get_text
from app.services.pedurma_reconstruction.reconstruction import get_preview_page

router = APIRouter()


@router.get("/{pecha_id}/texts/{text_id}", response_model=schemas.Text)
def read_text(pecha_id: str, text_id: str, page_no: Optional[int] = None):
    """
    Retrieve text from pecha
    """
    text = get_text(pecha_id, text_id)
    return text


@router.post("/save")
def save_text(text: schemas.Text):
    return f"Text {text.id} saved!"


@router.post("/preview", response_model=schemas.PedurmaPreviewPage)
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


@router.get("/{text_id}/notes", response_model=List[schemas.pecha.PedurmaNoteEdit])
def get_text_notes(text_id: str):
    notes = get_pedurma_text_edit_notes(text_id)
    return notes


@router.post("/{text_id}/notes")
def update_text_notes(text_id: str, notes: List[schemas.pecha.PedurmaNoteEdit]):
    update_text_pagination(text_id, notes)


@router.post("/{task_name}/completed", status_code=status.HTTP_201_CREATED)
def mark_text_completed(task_name: str, text_id: str):
    completed_texts_fn = Path.home() / ".openpecha" / task_name
    with completed_texts_fn.open("a") as fn:
        fn.write(f"{text_id}\n")
    return {"message": "Task marked as completed!"}


@router.get("/{task_name}/completed", response_model=List[Optional[str]])
def get_completed_texts(task_name: str):
    completed_texts_fn = Path.home() / ".openpecha" / task_name
    if not completed_texts_fn.is_file():
        return []
    return completed_texts_fn.read_text().splitlines()
