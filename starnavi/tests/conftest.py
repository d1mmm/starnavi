from datetime import datetime, timedelta
from unittest.mock import MagicMock

import jwt
import pytest
import vertexai
from starlette.testclient import TestClient

from starnavi.config import PROJECT_AI_ID, JWT_SECRET, ALGORITHM
from starnavi.database.db import get_session
from starnavi.main import app
from starnavi.services import credentials

vertexai.init(project=PROJECT_AI_ID, location="us-central1", credentials=credentials)


def generate_token():
    payload = {
        "email": "test@test.com",
        "exp": datetime.utcnow() + timedelta(minutes=5)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=ALGORITHM)
    return token


@pytest.fixture
def mock_session():
    session = MagicMock()

    def mock_add(instance):
        instance.id = 1
        instance.created_at = "2024-07-05T12:34:56"

    def mock_commit():
        pass

    session.add.side_effect = mock_add
    session.commit.side_effect = mock_commit
    return session


@pytest.fixture
def client(mock_session):
    app.dependency_overrides[get_session] = lambda: mock_session
    with TestClient(app) as c:
        yield c
