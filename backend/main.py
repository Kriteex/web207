# backend/main.py
from pydantic import BaseModel
from fastapi import FastAPI, File, UploadFile, Form
from backend.ads_api import fetch_campaigns, create_campaign, create_adset, upload_ad_image, create_adcreative
from backend.database import init_db
from fastapi.responses import JSONResponse
import os

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


class AdCreativeCreateRequest(BaseModel):
    account_id: str
    name: str
    title: str
    body: str
    object_url: str
    image_hash: str

@app.post("/create_adcreative")
async def api_create_adcreative(request: AdCreativeCreateRequest):
    result = await create_adcreative(
        account_id=request.account_id,
        name=request.name,
        title=request.title,
        body=request.body,
        object_url=request.object_url,
        image_hash=request.image_hash
    )
    return result



class AdCreateRequest(BaseModel):
    account_id: str
    adset_id: str
    creative_id: str
    name: str
    status: str

@app.post("/create_ad")
async def api_create_ad(req: AdCreateRequest):
    return await create_ad(req.account_id, req.adset_id,
                           req.creative_id, req.name, req.status)


@app.post("/upload_ad_image")
async def api_upload_ad_image(account_id: str = Form(...), file: UploadFile = File(...)):
    file_location = f"temp_{file.filename}"
    with open(file_location, "wb") as f:
        f.write(await file.read())
    result = await upload_ad_image(account_id, file_location)
    os.remove(file_location)
    return result