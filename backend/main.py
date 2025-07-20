# backend/main.py
from fastapi import FastAPI
from backend.ads_api import fetch_campaigns
from backend.database import init_db

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    await init_db()

@app.get("/campaigns")
async def get_campaigns():
    return await fetch_campaigns()