from typing import Generator

import pytest
from fastapi.testclient import TestClient
from pydantic import BaseSettings

from app.main import app
from app.core.config import get_settings


@pytest.fixture(scope="module")
def client() -> Generator:
    with TestClient(app) as client:
        yield client
    

@pytest.fixture(scope="session")
def settings() -> BaseSettings:
    return get_settings()
    
