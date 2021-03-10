from typing import Dict

from pydantic import BaseModel


class User(BaseModel):
    id: int
    username: str
    email: str


class BaseLayer(BaseModel):
    content: str


class AnnLayer(BaseModel):
    id: str
    annotation_type: str
    revision: str
    annotations: Dict
    local_ids: Dict
