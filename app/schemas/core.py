from typing import Dict, Optional

from pydantic import BaseModel


class BaseLayer(BaseModel):
    content: str


class AnnLayer(BaseModel):
    id: str
    annotation_type: str
    revision: str
    annotations: Dict
    local_ids: Dict
