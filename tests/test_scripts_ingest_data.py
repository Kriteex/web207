# tests/test_scripts_ingest_data.py
import asyncio

def test_ingest_calls_fetch(monkeypatch):
    called = {}
    async def fake_fetch(include_insights=False):
        called["include_insights"] = include_insights
        return [{"account_id": "1", "campaigns": []}]

    from scripts import ingest_data
    monkeypatch.setattr(ingest_data, "fetch_campaigns", fake_fetch)
    out = ingest_data.load_campaigns()
    assert called["include_insights"] is True
    assert out[0]["account_id"] == "1"
