# backend/ads_api.py
from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional, TypedDict

import httpx
from dotenv import load_dotenv

load_dotenv()

# Environment / constants ------------------------------------------------------

ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")
# Keep the original version to preserve behavior
BASE_URL = "https://graph.facebook.com/v23.0"

if not ACCESS_TOKEN:
    # Do not raise here – many callers import this module at import-time.
    # We'll check again in the request helpers and return a predictable JSON error.
    pass

# Business mapping retained verbatim (the frontend depends on these keys)
OBJECTIVE_OPTIMIZATION_MAP: Dict[str, List[str]] = {
    "OUTCOME_SALES": ["CONVERSIONS", "VALUE", "LANDING_PAGE_VIEWS"],
    "OUTCOME_TRAFFIC": ["LINK_CLICKS", "LANDING_PAGE_VIEWS"],
    "OUTCOME_ENGAGEMENT": ["POST_ENGAGEMENT", "PAGE_LIKES"],
    "OUTCOME_LEADS": ["LEAD_GENERATION", "CONVERSIONS"],
    "OUTCOME_APP_PROMOTION": ["APP_INSTALLS", "VALUE"],
    "OUTCOME_AWARENESS": ["REACH", "IMPRESSIONS"],
}


# Types ------------------------------------------------------------------------

class AdSummary(TypedDict, total=False):
    id: str
    name: str


class AdsetSummary(TypedDict, total=False):
    id: str
    name: str
    ads: List[AdSummary]


class CampaignSummary(TypedDict, total=False):
    id: str
    name: str
    objective: str
    # NOTE: "revenue" remains as in the original implementation,
    # but it is actually a ROAS ratio value from purchase_roas[0].value.
    spend: float
    revenue: float
    adsets: List[AdsetSummary]


# Private helpers --------------------------------------------------------------

def _missing_token_response() -> Dict[str, Any]:
    return {
        "error": {
            "message": "META_ACCESS_TOKEN is not set",
            "type": "config_error",
        }
    }


def _default_timeout() -> httpx.Timeout:
    # Reasonable client-side protection; does not change external behavior.
    return httpx.Timeout(connect=10.0, read=60.0, write=30.0, pool=10.0)


def _auth_params(extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    params = {"access_token": ACCESS_TOKEN}
    if extra:
        params.update(extra)
    return params


async def _get(client: httpx.AsyncClient, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Perform a GET to `{BASE_URL}/{path}` and return response.json()
    without raising. Keeps prior behavior: callers get Graph API JSON on
    both success and error.
    """
    if not ACCESS_TOKEN:
        return _missing_token_response()

    url = f"{BASE_URL}/{path.lstrip('/')}"
    resp = await client.get(url, params=_auth_params(params))
    # Preserve original semantics: return JSON even on non-2xx
    try:
        return resp.json()
    except Exception:
        return {"error": {"message": "Non-JSON response from Graph API", "status_code": resp.status_code}}


async def _post(
    client: httpx.AsyncClient,
    path: str,
    *,
    json_payload: Optional[Dict[str, Any]] = None,
    form_payload: Optional[Dict[str, Any]] = None,
    files: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Perform a POST to `{BASE_URL}/{path}` returning response.json().
    Mirrors the no-raise behavior of the original code.
    """
    if not ACCESS_TOKEN:
        return _missing_token_response()

    url = f"{BASE_URL}/{path.lstrip('/')}"
    # Attach token in the correct place (params for form, json for JSON)
    params = _auth_params()

    if json_payload is not None:
        # For JSON payloads, token should be in params to keep original pattern
        resp = await client.post(url, params=params, json=json_payload)
    else:
        # For form payloads, include token in form fields (original behavior)
        form_payload = form_payload or {}
        form_payload.setdefault("access_token", ACCESS_TOKEN)
        resp = await client.post(url, data=form_payload, files=files)

    try:
        return resp.json()
    except Exception:
        return {"error": {"message": "Non-JSON response from Graph API", "status_code": resp.status_code}}


# Public API -------------------------------------------------------------------

async def fetch_campaigns(include_insights: bool = False) -> List[Dict[str, Any]]:
    """
    Fetch accounts -> campaigns -> adsets -> ads.
    When include_insights is True, add 'spend' and 'revenue' (see note below).

    NOTE: The 'revenue' field retains original semantics: it is populated
    from `purchase_roas[0].value` (i.e., a ROAS ratio), not monetary revenue.
    The frontend depends on this exact shape/field name.
    """
    results: List[Dict[str, Any]] = []

    async with httpx.AsyncClient(timeout=_default_timeout()) as client:
        accounts_resp = await _get(client, "me/adaccounts")
        accounts = accounts_resp.get("data", []) or []

        for acc in accounts:
            acc_id = acc.get("id")
            if not acc_id:
                # Skip malformed entries but keep behavior predictable
                continue

            campaigns_resp = await _get(
                client,
                f"{acc_id}/campaigns",
                params={"fields": "id,name,objective"},
            )
            campaigns_data = campaigns_resp.get("data", []) or []
            campaigns: List[CampaignSummary] = []

            for campaign in campaigns_data:
                campaign_id = campaign.get("id")
                if not campaign_id:
                    continue

                # Enrich with insights if requested, else keep fields absent (originally absent)
                if include_insights:
                    insights_resp = await _get(
                        client,
                        f"{campaign_id}/insights",
                        params={"fields": "spend,purchase_roas"},
                    )
                    insights_list = insights_resp.get("data", []) or []
                    if insights_list:
                        first = insights_list[0]
                        spend = float(first.get("spend", 0) or 0.0)
                        roas_list = first.get("purchase_roas", []) or []
                        # See NOTE above: "revenue" remains a ROAS number for compatibility.
                        revenue = float(roas_list[0].get("value", 0)) if roas_list else 0.0
                    else:
                        spend = 0.0
                        revenue = 0.0

                    campaign["spend"] = spend
                    campaign["revenue"] = revenue

                # Fetch adsets
                adsets_resp = await _get(
                    client,
                    f"{campaign_id}/adsets",
                    params={"fields": "id,name"},
                )
                adsets_data = adsets_resp.get("data", []) or []
                adsets: List[AdsetSummary] = []

                for adset in adsets_data:
                    adset_id = adset.get("id")
                    if not adset_id:
                        continue

                    ads_resp = await _get(
                        client,
                        f"{adset_id}/ads",
                        params={"fields": "id,name"},
                    )
                    ads = ads_resp.get("data", []) or []
                    adset["ads"] = ads  # preserve original shape

                    adsets.append(adset)  # type: ignore[arg-type]

                campaign["adsets"] = adsets  # preserve original shape
                campaigns.append(campaign)    # type: ignore[arg-type]

            results.append({"account_id": acc_id, "campaigns": campaigns})

    return results


async def create_campaign(
    account_id: str,
    name: str,
    objective: str,
    status: str,
    special_ad_categories: List[str],
) -> Dict[str, Any]:
    """
    Create a campaign using the original payload contract.
    """
    payload = {
        "name": name,
        "objective": objective,
        "status": status,
        # Keep JSON string to preserve the original behavior
        "special_ad_categories": json.dumps(special_ad_categories),
    }
    async with httpx.AsyncClient(timeout=_default_timeout()) as client:
        return await _post(client, f"act_{account_id}/campaigns", form_payload=payload)


async def create_adset(
    account_id: str,
    campaign_id: str,
    name: str,
    daily_budget: int,
    optimization_goal: str,
    billing_event: str,
    bid_amount: int,
    targeting: Dict[str, Any],
    status: str,
) -> Dict[str, Any]:
    """
    Create an ad set. Preserves the original JSON layout (token in params).
    """
    payload = {
        "name": name,
        "campaign_id": campaign_id,
        "daily_budget": daily_budget,
        "optimization_goal": optimization_goal,
        "billing_event": billing_event,
        "bid_amount": bid_amount,
        "targeting": targeting,
        "status": status,
    }
    async with httpx.AsyncClient(timeout=_default_timeout()) as client:
        return await _post(client, f"act_{account_id}/adsets", json_payload=payload)


async def create_ad(
    account_id: str,
    adset_id: str,
    creative_id: str,
    name: str,
    status: str = "PAUSED",
) -> Dict[str, Any]:
    """
    Create an ad under a given ad set with a pre-existing creative.
    """
    payload = {
        "name": name,
        "adset_id": adset_id,
        "creative": {"creative_id": creative_id},
        "status": status,
    }
    async with httpx.AsyncClient(timeout=_default_timeout()) as client:
        return await _post(client, f"act_{account_id}/ads", json_payload=payload)


async def upload_ad_image(account_id: str, image_path: str) -> Dict[str, Any]:
    """
    Upload an image and return the Graph response (which includes image hash).
    """
    async with httpx.AsyncClient(timeout=_default_timeout()) as client:
        with open(image_path, "rb") as f:
            files = {"filename": (os.path.basename(image_path), f, "image/jpeg")}
            # Token goes into form data to match original behavior
            form = {"access_token": ACCESS_TOKEN}
            # Use raw path here to keep parity with original endpoint form
            url_path = f"act_{account_id}/adimages"
            url = f"{BASE_URL}/{url_path}"
            resp = await client.post(url, data=form, files=files)
            try:
                return resp.json()
            except Exception:
                return {"error": {"message": "Non-JSON response from Graph API", "status_code": resp.status_code}}


async def create_adcreative(
    account_id: str,
    name: str,
    title: str,
    body: str,
    object_url: str,
    image_hash: str,
) -> Dict[str, Any]:
    """
    Create a creative using object_story_spec with an image hash.
    Preserves the original approach (form-encoded with token in form).
    """
    payload = {
        "name": name,
        "title": title,
        "body": body,
        "object_story_spec": json.dumps(
            {
                "page_id": os.getenv("META_PAGE_ID"),
                "link_data": {
                    "message": body,
                    "link": object_url,
                    "image_hash": image_hash,
                },
            }
        ),
    }
    async with httpx.AsyncClient(timeout=_default_timeout()) as client:
        return await _post(client, f"act_{account_id}/adcreatives", form_payload=payload)
