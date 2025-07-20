# backend/ads_api.py
import httpx
import os
from dotenv import load_dotenv

load_dotenv()
ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")
BASE_URL = "https://graph.facebook.com/v19.0"

async def fetch_campaigns():
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BASE_URL}/me/adaccounts?access_token={ACCESS_TOKEN}")
        return resp.json()