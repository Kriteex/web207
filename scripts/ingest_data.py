# scripts/ingest_data.py
import asyncio
from backend.ads_api import fetch_campaigns

def load_campaigns():
    raw = asyncio.run(fetch_campaigns())
    return raw


