from typing import List, Optional

from pydantic import BaseModel


# Shared properties
class PageBase(BaseModel):
    id: str
    page_no: int
    content: str
    name: str
    vol: str
    image_link: Optional[str] = None


class Page(PageBase):
    note_ref: Optional[str]


class NotesPage(PageBase):
    pass


class Text(BaseModel):
    id: str
    pages: List[Page]
    notes: Optional[List[NotesPage]]


class PedurmaPreviewPage(BaseModel):
    content: str


class PedurmaNoteEdit(BaseModel):
    image_link: str
    page_no: int
    ref_start_page_no: int
    ref_end_page_no: int
