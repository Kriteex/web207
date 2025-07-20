# backend/ads_api.py
import httpx
import os
from dotenv import load_dotenv

load_dotenv()
ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")
BASE_URL = "https://graph.facebook.com/v19.0"

async def fetch_campaigns():
    async with httpx.AsyncClient() as client:
        accounts_resp = await client.get(f"{BASE_URL}/me/adaccounts?access_token={ACCESS_TOKEN}")
        accounts = accounts_resp.json().get("data", [])

        results = []
        for acc in accounts:
            acc_id = acc["id"]
            campaigns_resp = await client.get(
                f"{BASE_URL}/{acc_id}/campaigns?access_token={ACCESS_TOKEN}&fields=id,name,objective"
            )
            campaigns = campaigns_resp.json().get("data", [])

            for campaign in campaigns:
                campaign_id = campaign["id"]
                adsets_resp = await client.get(
                    f"{BASE_URL}/{campaign_id}/adsets?access_token={ACCESS_TOKEN}&fields=id,name"
                )
                adsets = adsets_resp.json().get("data", [])

                for adset in adsets:
                    adset_id = adset["id"]
                    ads_resp = await client.get(
                        f"{BASE_URL}/{adset_id}/ads?access_token={ACCESS_TOKEN}&fields=id,name"
                    )
                    ads = ads_resp.json().get("data", [])

                    adset["ads"] = ads

                campaign["adsets"] = adsets

            results.append({"account_id": acc_id, "campaigns": campaigns})

        return results