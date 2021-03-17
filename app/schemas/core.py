from typing import Optional

from pydantic import BaseModel


class User(BaseModel):
    id: int
    username: str
    email: Optional[str] = ""


class BaseLayer(BaseModel):
    content: str
