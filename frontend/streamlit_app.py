# frontend/streamlit_app.py
import streamlit as st
import sys
import os
import json
import requests
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from scripts.ingest_data import load_campaigns
from frontend.utils import display_campaigns

# Přesunutá mapa do frontendu
OBJECTIVE_OPTIMIZATION_MAP = {
    "OUTCOME_SALES": ["CONVERSIONS", "VALUE", "LANDING_PAGE_VIEWS"],
    "OUTCOME_TRAFFIC": ["LINK_CLICKS", "LANDING_PAGE_VIEWS"],
    "OUTCOME_ENGAGEMENT": ["POST_ENGAGEMENT", "PAGE_LIKES"],
    "OUTCOME_LEADS": ["LEAD_GENERATION", "CONVERSIONS"],
    "OUTCOME_APP_PROMOTION": ["APP_INSTALLS", "VALUE"],
    "OUTCOME_AWARENESS": ["REACH", "IMPRESSIONS"]
}

st.title("Madgicx MVP Dashboard")

if st.button("Načíst kampaně", key="load_campaigns_button"):
    data = load_campaigns()
    display_campaigns(data)

st.markdown("---")
st.subheader("🚀 Vytvořit novou kampaň")

with st.form("create_campaign_form"):
    account_id = st.text_input("Ad Account ID (bez 'act_')", key="campaign_account")
    campaign_name = st.text_input("Název kampaně", key="campaign_name")
    objective = st.selectbox("Cíl kampaně", list(OBJECTIVE_OPTIMIZATION_MAP.keys()), key="campaign_objective")
    status = st.selectbox("Stav", ["PAUSED", "ACTIVE"], key="campaign_status")
    special_ad_categories = st.multiselect(
        "Special Ad Categories (např. HOUSING, EMPLOYMENT, CREDIT)",
        ["NONE", "HOUSING", "EMPLOYMENT", "CREDIT"],
        default=["NONE"],
        key="campaign_special"
    )
    submit_campaign = st.form_submit_button("Vytvořit kampaň")

    if submit_campaign:
        res = requests.post(
            "http://localhost:8000/create_campaign",
            json={
                "account_id": account_id,
                "name": campaign_name,
                "objective": objective,
                "status": status,
                "special_ad_categories": [] if "NONE" in special_ad_categories else special_ad_categories
            }
        )
        if res.status_code == 200:
            st.success(f"Kampaň vytvořena: {res.json()}")
        else:
            st.error(f"Chyba: {res.text}")

st.markdown("---")
st.subheader("📦 Vytvořit nový ad set")

# Dynamické UI s rerenderem mimo form kvůli aktualizaci valid_goals
selected_objective = st.selectbox("Objective kampaně pro ad set", list(OBJECTIVE_OPTIMIZATION_MAP.keys()), key="adset_objective")
valid_goals = OBJECTIVE_OPTIMIZATION_MAP.get(selected_objective, [])

with st.form("create_adset_form"):
    account_id = st.text_input("Ad Account ID (bez 'act_')", key="adset_account")
    campaign_id = st.text_input("Campaign ID", key="adset_campaign")
    adset_name = st.text_input("Název Ad Setu", key="adset_name")
    daily_budget = st.number_input("Denní rozpočet (v centích)", min_value=100, key="adset_budget")
    billing_event = st.selectbox("Billing Event", ["IMPRESSIONS", "CLICKS", "LINK_CLICKS"], key="adset_billing")
    country = st.text_input("Země cílení (např. US)", value="US", key="adset_country")
    optimization_goal = st.selectbox("Optimalizační cíl", valid_goals, key="adset_optimization")
    bid_amount = st.number_input("Bid Amount (v centích)", min_value=1, key="adset_bid")

    submit_adset = st.form_submit_button("Vytvořit Ad Set")

    if submit_adset:
        res = requests.post(
            "http://localhost:8000/create_adset",
            json={
                "account_id": account_id,
                "campaign_id": campaign_id,
                "name": adset_name,
                "daily_budget": daily_budget,
                "optimization_goal": optimization_goal,
                "billing_event": billing_event,
                "bid_amount": bid_amount,
                "targeting": {
                    "geo_locations": {"countries": [country]}
                },
                "status": "PAUSED"
            }
        )
        if res.status_code == 200:
            st.success(f"Ad Set vytvořen: {res.json()}")
        else:
            st.error(f"Chyba: {res.text}")
