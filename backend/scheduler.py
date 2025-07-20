# backend/scheduler.py
import schedule
import time
from backend.ads_api import fetch_campaigns

async def scheduled_job():
    campaigns = await fetch_campaigns()
    print("Fetched campaigns:", campaigns)

schedule.every(1).hours.do(lambda: scheduled_job())

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

