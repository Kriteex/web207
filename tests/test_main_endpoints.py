# tests/test_main_endpoints.py
from io import BytesIO
from unittest.mock import AsyncMock

def test_get_campaigns_endpoint_calls_fetch(app_client, monkeypatch):
    called = {}

    async def fake_fetch(include_insights: bool = False):
        called["include_insights"] = include_insights
        return [{"account_id": "1", "campaigns": []}]

    from backend import main as backend_main
    monkeypatch.setattr(backend_main, "fetch_campaigns", fake_fetch)

    r = app_client.get("/campaigns?include_insights=true")
    assert r.status_code == 200
    assert called["include_insights"] is True
    assert r.json()[0]["account_id"] == "1"


def test_create_campaign_endpoint(app_client, monkeypatch):
    async def fake_create(**kwargs):
        return {"id": "camp_123", **kwargs}

    from backend import main as backend_main
    monkeypatch.setattr(backend_main, "create_campaign", fake_create)

    payload = {
        "account_id": "1",
        "name": "Camp",
        "objective": "OUTCOME_SALES",
        "status": "PAUSED",
        "special_ad_categories": [],
    }
    r = app_client.post("/create_campaign", json=payload)
    assert r.status_code == 200
    assert r.json()["id"] == "camp_123"


def test_upload_image_endpoint(app_client, monkeypatch):
    async def fake_upload(account_id: str, image_path: str):
        assert account_id == "1"
        # soubor byl uložen dočasně na disk – jen vrátíme hash
        return {"images": {"temp_file.jpg": {"hash": "H"}}}

    from backend import main as backend_main
    monkeypatch.setattr(backend_main, "upload_ad_image", fake_upload)

    file = BytesIO(b"abc")
    file.name = "file.jpg"
    r = app_client.post(
        "/upload_ad_image",
        data={"account_id": "1"},
        files={"file": ("file.jpg", file, "image/jpeg")},
    )
    assert r.status_code == 200
    assert "images" in r.json()
