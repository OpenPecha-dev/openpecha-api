from typing import Dict

from pydantic import BaseModel


class BaseLayer(BaseModel):
    id: str
    content: str


class AnnLayer(BaseModel):
    id: str
    annotation_type: str
    revision: str
    annotations: Dict
    local_ids: Dict
