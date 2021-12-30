from pydantic import BaseModel


class DiffInput(BaseModel):
    textA: str
    textB: str
