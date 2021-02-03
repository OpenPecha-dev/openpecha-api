import pytest
from fastapi.testclient import TestClient
from pydantic import BaseSettings
from starlette import responses

from app import schemas


@pytest.mark.skip(reason="need mocking")
def test_get_text(client: TestClient, settings: BaseSettings) -> None:
    pecha_id = "P000792"
    text_id = "T-1"

    response = client.get(f"{settings.API_V1_STR}/{pecha_id}/texts/{text_id}")

    assert response.status_code == 200
    content = response.json()
    assert content["id"] == text_id
    assert content["pages"]
    assert content["notes"]
