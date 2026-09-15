"""Tests for AI API dynamic configuration and endpoints."""

import pytest
from fastapi.testclient import TestClient
from living_universe.web.server import app, engine
from living_universe.ai.pantheon import QuadAIPantheon


@pytest.fixture
def client():
    return TestClient(app)


def test_ai_config_get(client):
    res = client.get("/api/ai_config")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert "providers" in data
    assert "gemini" in data["providers"]
    assert "groq" in data["providers"]
    assert "openai" in data["providers"]


def test_ai_config_post(client):
    res = client.post(
        "/api/ai_config",
        json={
            "gemini_api_key": "AIzaSyTestKey123",
            "groq_api_key": "gsk_TestGroqKey456",
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert "configured" in data


def test_pantheon_configure_api_keys():
    pantheon = QuadAIPantheon(interval_seconds=100.0)
    res = pantheon.configure_api_keys(
        gemini_key="AIzaSyTestDummyKey",
        groq_key="gsk_TestDummyKey",
    )
    assert isinstance(res, dict)
    assert "gemini" in res
    assert "groq" in res
