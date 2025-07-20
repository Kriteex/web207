# backend/main.py
from fastapi import FastAPI, Form
from backend.ads_api import fetch_campaigns, create_campaign
from backend.database import init_db

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    await init_db()

@app.get("/campaigns")
async def get_campaigns():
    return await fetch_campaigns()

@app.post("/create_campaign")
async def api_create_campaign(
    account_id: str = Form(...),
    name: str = Form(...),
    objective: str = Form("CONVERSIONS"),
    status: str = Form("PAUSED")
):
    return await create_campaign(account_id, name, objective, status)