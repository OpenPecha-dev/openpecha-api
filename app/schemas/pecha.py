from typing import List, Optional

from pydantic import BaseModel


# Shared properties
class PageBase(BaseModel):
    id: str
    page_no: int
    content: str


class Page(PageBase):
    name: str
    notes_page_id: Optional[str]


class NotesPage(PageBase):
    pass


class Text(BaseModel):
    id: str
    pages: List[Page]
    notes: Optional[List[NotesPage]]
