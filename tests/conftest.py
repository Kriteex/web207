# tests/conftest.py
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import importlib
import json
import asyncio
import io
import types
from typing import AsyncIterator

import pytest
import respx
from httpx import Response
from fastapi.testclient import TestClient

# --- Základní env pro testy ---
@pytest.fixture(autouse=True)
def test_env(monkeypatch, tmp_path):
    monkeypatch.setenv("META_ACCESS_TOKEN", "test-meta-token")
    monkeypatch.setenv("META_PAGE_ID", "1234567890")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    # Pro init_db testy budeme přepínat, defaultně ale nastavíme funkční SQLite URL
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{tmp_path/'test.db'}")
    yield


# --- respx router pro mocking Graph API ---
@pytest.fixture
def graph_mock():
    with respx.mock(base_url="https://graph.facebook.com/v23.0") as router:
        yield router


# --- FastAPI TestClient s vypnutou DB init (startup) ---
@pytest.fixture
def app_client(monkeypatch):
    # Import backend.main až po nastavení env
    from backend import main as backend_main

    async def _no_db():
        return None

    monkeypatch.setattr(backend_main, "init_db", _no_db)
    client = TestClient(backend_main.app)
    return client


# --- Pomocná fixtura: event loop pro pytest-asyncio (strict mode) ---
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()
