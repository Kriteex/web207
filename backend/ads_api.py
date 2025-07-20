import httpx
import json
import os
from dotenv import load_dotenv

load_dotenv()
ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")
BASE_URL = "https://graph.facebook.com/v17.0"

# Mapování kampaně → optimalizační cíle
OBJECTIVE_OPTIMIZATION_MAP = {
    "OUTCOME_SALES": ["CONVERSIONS", "VALUE", "LANDING_PAGE_VIEWS"],
    "OUTCOME_TRAFFIC": ["LINK_CLICKS", "LANDING_PAGE_VIEWS"],
    "OUTCOME_ENGAGEMENT": ["POST_ENGAGEMENT", "PAGE_LIKES"],
    "OUTCOME_LEADS": ["LEAD_GENERATION", "CONVERSIONS"],
    "OUTCOME_APP_PROMOTION": ["APP_INSTALLS", "VALUE"],
    "OUTCOME_AWARENESS": ["REACH", "IMPRESSIONS"]
}

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

async def create_campaign(account_id: str, name: str, objective: str, status: str, special_ad_categories: list):
    url = f"{BASE_URL}/act_{account_id}/campaigns"
    payload = {
        "name": name,
        "objective": objective,
        "status": status,
        "special_ad_categories": json.dumps(special_ad_categories),
        "access_token": ACCESS_TOKEN
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, data=payload)
        return resp.json()

async def create_adset(account_id: str, campaign_id: str, name: str, daily_budget: int, optimization_goal: str, billing_event: str, bid_amount: int, targeting: dict, status: str):
    url = f"{BASE_URL}/act_{account_id}/adsets"
    payload = {
        "name": name,
        "campaign_id": campaign_id,
        "daily_budget": daily_budget,
        "optimization_goal": optimization_goal,
        "billing_event": billing_event,
        "bid_amount": bid_amount,
        "targeting": targeting,
        "status": status,
        "access_token": ACCESS_TOKEN
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json=payload)
        return resp.json()
