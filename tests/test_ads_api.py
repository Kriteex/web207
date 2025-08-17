# nahoře
import json
import pytest
import respx
from httpx import Response
from backend import ads_api

@pytest.mark.asyncio
async def test_get_without_token(monkeypatch):
    # Zneplatni token v env i v modulu
    monkeypatch.delenv("META_ACCESS_TOKEN", raising=False)
    monkeypatch.setattr(ads_api, "ACCESS_TOKEN", None, raising=False)

    async with ads_api.httpx.AsyncClient(timeout=ads_api._default_timeout()) as client:
        out = await ads_api._get(client, "me/adaccounts")
    assert out["error"]["type"] == "config_error"

@pytest.mark.asyncio
async def test_post_without_token(monkeypatch):
    monkeypatch.delenv("META_ACCESS_TOKEN", raising=False)
    monkeypatch.setattr(ads_api, "ACCESS_TOKEN", None, raising=False)

    async with ads_api.httpx.AsyncClient(timeout=ads_api._default_timeout()) as client:
        out = await ads_api._post(client, "x/y", json_payload={"a": 1})
    assert out["error"]["type"] == "config_error"


@pytest.mark.asyncio
async def test_fetch_campaigns_happy_path(graph_mock):
    # /me/adaccounts
    graph_mock.get("/me/adaccounts").respond(
        200, json={"data": [{"id": "act_1".replace("act_", "")}]}
    )
    # /{acc}/campaigns
    graph_mock.get("/1/campaigns").respond(
        200, json={"data": [{"id": "c1", "name": "C1", "objective": "OUTCOME_SALES"}]}
    )
    # insights (spend + purchase_roas)
    graph_mock.get("/c1/insights").respond(
        200, json={"data": [{"spend": "123.45", "purchase_roas": [{"value": "2.5"}]}]}
    )
    # adsets
    graph_mock.get("/c1/adsets").respond(
        200, json={"data": [{"id": "s1", "name": "S1"}]}
    )
    # ads
    graph_mock.get("/s1/ads").respond(
        200, json={"data": [{"id": "a1", "name": "A1"}]}
    )

    out = await ads_api.fetch_campaigns(include_insights=True)
    assert out and out[0]["account_id"] == "1"
    camp = out[0]["campaigns"][0]
    assert camp["id"] == "c1"
    assert camp["spend"] == 123.45
    # revenue pole je skutečně ROAS (poměr), dle poznámky v kódu:
    assert camp["revenue"] == 2.5
    assert camp["adsets"][0]["ads"][0]["id"] == "a1"


@pytest.mark.asyncio
async def test_fetch_campaigns_without_insights(graph_mock):
    graph_mock.get("/me/adaccounts").respond(200, json={"data": [{"id": "1"}]})
    graph_mock.get("/1/campaigns").respond(200, json={"data": [{"id": "c1", "name": "C1"}]})
    graph_mock.get("/c1/adsets").respond(200, json={"data": []})

    out = await ads_api.fetch_campaigns(include_insights=False)
    camp = out[0]["campaigns"][0]
    assert "spend" not in camp
    assert "revenue" not in camp


@pytest.mark.asyncio
async def test_create_campaign_form_payload(graph_mock):
    def _assert_form(request):
        form = request.content.decode()
        assert "name=MyCamp" in form
        assert "objective=OUTCOME_SALES" in form
        assert "status=PAUSED" in form
        assert "special_ad_categories=%5B%22NONE%22%5D" in form  # JSON-encoded
        assert "access_token=" in form
        return Response(200, json={"id": "new_campaign"})

    graph_mock.post("/act_1/campaigns").mock(side_effect=_assert_form)
    out = await ads_api.create_campaign(
        account_id="1",
        name="MyCamp",
        objective="OUTCOME_SALES",
        status="PAUSED",
        special_ad_categories=["NONE"],
    )
    assert out["id"] == "new_campaign"


@pytest.mark.asyncio
async def test_create_adset_json_payload(graph_mock):
    def _assert_json(request):
        # token v URL parametrech
        assert "access_token" in request.url.params
        # JSON tělo
        data = json.loads(request.content.decode())
        assert data["campaign_id"] == "c1"
        assert data["optimization_goal"] == "CONVERSIONS"
        assert data["targeting"] == {"geo_locations": {"countries": ["US"]}}
        return Response(200, json={"id": "new_adset"})

    graph_mock.post("/act_1/adsets").mock(side_effect=_assert_json)
    out = await ads_api.create_adset(
        account_id="1",
        campaign_id="c1",
        name="S1",
        daily_budget=1000,
        optimization_goal="CONVERSIONS",
        billing_event="IMPRESSIONS",
        bid_amount=10,
        targeting={"geo_locations": {"countries": ["US"]}},
        status="PAUSED",
    )
    assert out["id"] == "new_adset"


@pytest.mark.asyncio
async def test_create_ad_json_payload(graph_mock):
    def _assert_json(request):
        assert "access_token" in request.url.params
        data = json.loads(request.content.decode())
        assert data["adset_id"] == "s1"
        assert data["creative"] == {"creative_id": "cr1"}
        assert data["status"] == "PAUSED"
        return Response(200, json={"id": "new_ad"})

    graph_mock.post("/act_1/ads").mock(side_effect=_assert_json)
    out = await ads_api.create_ad(
        account_id="1",
        adset_id="s1",
        creative_id="cr1",
        name="AdName",
        status="PAUSED",
    )
    assert out["id"] == "new_ad"



@pytest.mark.asyncio
async def test_upload_ad_image_form(graph_mock, tmp_path, monkeypatch):
    img_path = tmp_path / "x.jpg"
    img_path.write_bytes(b"\xff\xd8\xff")  # fake JPEG

    def _assert_upload(request):
        # V date musí být access_token, soubor ve files
        assert b"access_token" in request.content
        return Response(200, json={"images": {"x.jpg": {"hash": "IMGHASH"}}})

    graph_mock.post("/act_1/adimages").mock(side_effect=_assert_upload)

    out = await ads_api.upload_ad_image("1", str(img_path))
    assert out["images"]["x.jpg"]["hash"] == "IMGHASH"


from urllib.parse import parse_qs

@pytest.mark.asyncio
async def test_create_adcreative_form_payload(graph_mock, monkeypatch):
    monkeypatch.setenv("META_PAGE_ID", "999")

    def _assert_form(request):
        form_raw = request.content.decode()
        form = parse_qs(form_raw)

        # Jednotlivá pole
        assert form["name"] == ["MyCreative"]
        assert form["title"] == ["Title"]
        assert form["body"] == ["Body"]

        # object_story_spec je URL-decoded JSON string → rozparsovat
        spec = json.loads(form["object_story_spec"][0])
        assert spec["page_id"] == "999"
        assert spec["link_data"]["image_hash"] == "HASH123"
        assert spec["link_data"]["link"]  # je tam nějaký link
        return Response(200, json={"id": "cr_new"})

    graph_mock.post("/act_1/adcreatives").mock(side_effect=_assert_form)

    out = await ads_api.create_adcreative(
        account_id="1",
        name="MyCreative",
        title="Title",
        body="Body",
        object_url="https://ex.com",
        image_hash="HASH123",
    )
    assert out["id"] == "cr_new"