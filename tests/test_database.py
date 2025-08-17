# tests/test_database.py
import importlib
import asyncio
import pytest

def test_init_db_without_url(monkeypatch):
    # Nastav prázdnou hodnotu, aby ji load_dotenv nepřepsal (override=False)
    monkeypatch.setenv("DATABASE_URL", "")
    from backend import database
    importlib.reload(database)

    with pytest.raises(RuntimeError):
        asyncio.run(database.init_db())


def test_init_db_with_sqlite(monkeypatch, tmp_path):
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{tmp_path/'ok.db'}")
    from backend import database
    importlib.reload(database)
    asyncio = __import__("asyncio")
    asyncio.run(database.init_db())
