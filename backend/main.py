# backend/main.py
from pydantic import BaseModel
from fastapi import FastAPI, Form
from backend.ads_api import fetch_campaigns, create_campaign, create_adset
from backend.database import init_db

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    await init_db()

@app.get("/campaigns")
async def get_campaigns():
    return await fetch_campaigns()

class CampaignCreateRequest(BaseModel):
    account_id: str
    name: str
    objective: str
    status: str
    special_ad_categories: list

@app.post("/create_campaign")
async def api_create_campaign(request: CampaignCreateRequest):
    return await create_campaign(
        account_id=request.account_id,
        name=request.name,
        objective=request.objective,
        status=request.status,
        special_ad_categories=request.special_ad_categories
    )


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

@app.post("/create_adset")
async def api_create_adset(request: AdSetCreateRequest):
    result = await create_adset(
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
    return result