from typing import List, Tuple

from pydantic import AnyHttpUrl, BaseModel


class ProofreadPage(BaseModel):
    content: str
    image_url: AnyHttpUrl


class PageDiff(BaseModel):
    diffs: List[Tuple[int, str]]


class IIIFImageUrl(BaseModel):
    image_url: AnyHttpUrl


class ProjectMetadata(BaseModel):
    versions: List[str]
    proofreading_version: str


class VersionMetadata(BaseModel):
    pages: List[str]
