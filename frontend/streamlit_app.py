# frontend/streamlit_app.py
import streamlit as st
import sys
import os
import requests
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from scripts.ingest_data import load_campaigns
from frontend.utils import display_campaigns


import requests
from scripts.ingest_data import load_campaigns
from frontend.utils import display_campaigns

st.title("Madgicx MVP Dashboard")

if st.button("Načíst kampaně"):
    data = load_campaigns()
    display_campaigns(data)

st.markdown("---")
st.subheader("🚀 Vytvořit novou kampaň")

with st.form("create_campaign_form"):
    account_id = st.text_input("Ad Account ID (bez 'act_')")
    name = st.text_input("Název kampaně")
    valid_objectives = [
        "OUTCOME_SALES", "OUTCOME_TRAFFIC", "OUTCOME_ENGAGEMENT",
        "LEAD_GENERATION", "VIDEO_VIEWS", "REACH", "BRAND_AWARENESS"
    ]
    objective = st.selectbox("Cíl kampaně", valid_objectives)
    status = st.selectbox("Stav", ["PAUSED", "ACTIVE"])
    submit = st.form_submit_button("Vytvořit")

    if submit:
        res = requests.post(
            "http://localhost:8000/create_campaign",
            data={
                "account_id": account_id,
                "name": name,
                "objective": objective,
                "status": status
            }
        )
        if res.status_code == 200:
            st.success(f"Kampaň vytvořena: {res.json()}")
        else:
            st.error(f"Chyba: {res.text}")

