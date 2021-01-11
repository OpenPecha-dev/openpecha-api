from typing import List, Optional

from fastapi import APIRouter

from app import schemas

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
    content = (
        f"<p>This Page preview google page {google_page.page_no}</p>"
        f"<p>{google_page.content}</p>"
    )
    return schemas.PedurmaPreviewPage(content=content)


@router.get(
    "/pedurma/{text_id}/notes", response_model=List[schemas.pecha.PedurmaNoteEdit]
)
def get_text_notes(text_id: str):
    notes = [
        schemas.pecha.PedurmaNoteEdit(
            image_link="https://www.tbrc.org/browser/ImageService?work=W1PD96682&igroup=I1PD96839&image=504&first=1&last=2000&fetchimg=yes",
            page_no=50,
            ref_start_page_no=10,
            ref_end_page_no=15,
        ),
        schemas.pecha.PedurmaNoteEdit(
            image_link="https://www.tbrc.org/browser/ImageService?work=W1PD96682&igroup=I1PD96839&image=505&first=1&last=2000&fetchimg=yes",
            page_no=51,
            ref_start_page_no=16,
            ref_end_page_no=20,
        ),
        schemas.pecha.PedurmaNoteEdit(
            image_link="https://www.tbrc.org/browser/ImageService?work=W1PD96682&igroup=I1PD96839&image=525&first=1&last=2000&fetchimg=yes",
            page_no=52,
            ref_start_page_no=21,
            ref_end_page_no=25,
        ),
    ]
    return notes


@router.post("/pedurma/{text_id}/notes")
def update_text_notes(notes: List[schemas.pecha.PedurmaNoteEdit]):
    print(notes)
    return notes
