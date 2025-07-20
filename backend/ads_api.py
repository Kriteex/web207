# backend/ads_api.py
import httpx
import os
from dotenv import load_dotenv
import json

load_dotenv()
ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")
BASE_URL = "https://graph.facebook.com/v19.0"

async def fetch_campaigns(include_insights=False):
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

                if include_insights:
                    insights_resp = await client.get(
                        f"{BASE_URL}/{campaign_id}/insights?access_token={ACCESS_TOKEN}&fields=spend,purchase_roas"
                    )
                    insights_data = insights_resp.json().get("data", [])
                    if insights_data:
                        insights = insights_data[0]
                        campaign["spend"] = float(insights.get("spend", 0))
                        roas = insights.get("purchase_roas", [])
                        campaign["revenue"] = float(roas[0].get("value", 0)) if roas else 0
                    else:
                        campaign["spend"] = 0.0
                        campaign["revenue"] = 0.0

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


async def create_campaign(account_id: str, name: str, objective: str = "OUTCOME_SALES", status: str = "PAUSED"):
    url = f"{BASE_URL}/act_{account_id}/campaigns"
    params = {
        "access_token": ACCESS_TOKEN,
        "name": name,
        "objective": objective,
        "status": status,
        "special_ad_categories": json.dumps([])  # musí být jako JSON-encoded string
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, data=params)
        return resp.json()