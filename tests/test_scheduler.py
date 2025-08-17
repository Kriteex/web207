# tests/test_scheduler.py
import asyncio
from backend import scheduler

def test_run_fetch_campaigns_sync_logs(monkeypatch, capsys):
    async def fake_fetch_campaigns():
        return [{"account_id": "1", "campaigns": []}]

    monkeypatch.setattr(scheduler, "fetch_campaigns", fake_fetch_campaigns)
    scheduler._run_fetch_campaigns_sync()
    out = capsys.readouterr().out
    assert "Fetched campaigns:" in out
