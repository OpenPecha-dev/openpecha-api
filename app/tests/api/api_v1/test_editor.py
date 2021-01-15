from fastapi.testclient import TestClient
from starlette import responses

from pydantic import BaseSettings

from app import schemas



def test_get_text(client: TestClient, settings: BaseSettings) -> None:
    pecha_id = "P0000001"
    text_id = "T-1"

    response = client.get(f"{settings.API_V1_STR}/{pecha_id}/texts/{text_id}")

    assert response.status_code == 200
    content = response.json()
    assert content["id"] == text_id
    assert content["pages"]
    assert content["notes"]
