# backend/main.py
from __future__ import annotations

import os
from typing import Any, Dict, List

from fastapi import FastAPI, File, Form, UploadFile
from pydantic import BaseModel

from backend.ads_api import (
    create_ad,
    create_adcreative,
    create_adset,
    create_campaign,
    fetch_campaigns,
    upload_ad_image,
)
from backend.database import init_db

app = FastAPI(title="Madgicx MVP Backend")


@app.on_event("startup")
async def startup_event() -> None:
    await init_db()


# ------------------------------------------------------------------------------
# Campaigns
# ------------------------------------------------------------------------------

@app.get("/campaigns", tags=["campaigns"])
async def get_campaigns(include_insights: bool = False) -> List[Dict[str, Any]]:
    """
    Fetch all accounts and their campaigns/adsets/ads.
    - `include_insights`: when true, include spend and 'revenue' (ROAS ratio value).
    """
    return await fetch_campaigns(include_insights=include_insights)


class CampaignCreateRequest(BaseModel):
    account_id: str
    name: str
    objective: str
    status: str
    special_ad_categories: list


@app.post("/create_campaign", tags=["campaigns"])
async def api_create_campaign(request: CampaignCreateRequest) -> Dict[str, Any]:
    return await create_campaign(
        account_id=request.account_id,
        name=request.name,
        objective=request.objective,
        status=request.status,
        special_ad_categories=request.special_ad_categories,
    )


# ------------------------------------------------------------------------------
# Ad Sets
# ------------------------------------------------------------------------------

class AdSetCreateRequest(BaseModel):
    account_id: str
    campaign_id: str
    name: str
    daily_budget: int
    optimization_goal: str
    billing_event: str
    bid_amount: int
    targeting: dict
    status: str


@app.post("/create_adset", tags=["adsets"])
async def api_create_adset(request: AdSetCreateRequest) -> Dict[str, Any]:
    return await create_adset(
        account_id=request.account_id,
        campaign_id=request.campaign_id,
        name=request.name,
        daily_budget=request.daily_budget,
        optimization_goal=request.optimization_goal,
        billing_event=request.billing_event,
        bid_amount=request.bid_amount,
        targeting=request.targeting,
        status=request.status,
    )


# ------------------------------------------------------------------------------
# Creatives
# ------------------------------------------------------------------------------

class AdCreativeCreateRequest(BaseModel):
    account_id: str
    name: str
    title: str
    body: str
    object_url: str
    image_hash: str


@app.post("/create_adcreative", tags=["creatives"])
async def api_create_adcreative(request: AdCreativeCreateRequest) -> Dict[str, Any]:
    """
    Create an ad creative (image_hash based link ad).
    """
    return await create_adcreative(
        account_id=request.account_id,
        name=request.name,
        title=request.title,
        body=request.body,
        object_url=request.object_url,
        image_hash=request.image_hash,
    )


# ------------------------------------------------------------------------------
# Ads
# ------------------------------------------------------------------------------

class AdCreateRequest(BaseModel):
    account_id: str
    adset_id: str
    creative_id: str
    name: str
    status: str


@app.post("/create_ad", tags=["ads"])
async def api_create_ad(req: AdCreateRequest) -> Dict[str, Any]:
    return await create_ad(
        req.account_id,
        req.adset_id,
        req.creative_id,
        req.name,
        req.status,
    )


# ------------------------------------------------------------------------------
# Asset upload
# ------------------------------------------------------------------------------

@app.post("/upload_ad_image", tags=["assets"])
async def api_upload_ad_image(
    account_id: str = Form(...),
    file: UploadFile = File(...),
) -> Dict[str, Any]:
    """
    Upload image to the ad account library and return Graph response (image hash).
    """
    # Store temporarily on disk; keep original approach and filename behavior.
    file_location = f"temp_{file.filename}"
    with open(file_location, "wb") as f:
        f.write(await file.read())

    try:
        result = await upload_ad_image(account_id, file_location)
    finally:
        try:
            os.remove(file_location)
        except OSError:
            # Best-effort cleanup; do not change API behavior if deletion fails.
            pass

    return result
