# frontend/streamlit_app.py
import streamlit as st
import sys
import os
import json
import requests
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from scripts.ingest_data import load_campaigns
from frontend.utils import display_campaigns

API_BASE = "http://localhost:8000"

def fetch_campaigns_via_api(include_insights: bool = False):
    # backend /campaigns param momentálně neřeší, takže ho neposíláme
    resp = requests.get(f"{API_BASE}/campaigns", timeout=60)
    resp.raise_for_status()
    return resp.json()

# Přesunutá mapa do frontendu
OBJECTIVE_OPTIMIZATION_MAP = {
    "OUTCOME_SALES": ["CONVERSIONS", "VALUE", "LANDING_PAGE_VIEWS"],
    "OUTCOME_TRAFFIC": ["LINK_CLICKS", "LANDING_PAGE_VIEWS"],
    "OUTCOME_ENGAGEMENT": ["POST_ENGAGEMENT", "PAGE_LIKES"],
    "OUTCOME_LEADS": ["LEAD_GENERATION", "CONVERSIONS"],
    "OUTCOME_APP_PROMOTION": ["APP_INSTALLS", "VALUE"],
    "OUTCOME_AWARENESS": ["REACH", "IMPRESSIONS"]
}

# Layout + sidebar
st.set_page_config(page_title="Madgicx MVP Dashboard", layout="wide")
st.sidebar.title("📊 Menu")
page = st.sidebar.radio("Vyber sekci", ["Ads Dashboard", "Ads Management", "Ads Library"])

# -------------------------
# ADS DASHBOARD
# -------------------------
if page == "Ads Dashboard":
    st.title("Madgicx MVP Dashboard – 📈 Ads Dashboard")

    # Kampaně
    if "campaigns_data" not in st.session_state:
        st.session_state["campaigns_data"] = None

    if st.button("Načíst kampaně", key="load_campaigns_button"):
        with st.spinner("Načítám kampaně…"):
            try:
                st.session_state["campaigns_data"] = fetch_campaigns_via_api(include_insights=True)
            except Exception as e:
                st.error("Nepodařilo se načíst kampaně.")
                st.exception(e)

    if st.session_state["campaigns_data"]:
        display_campaigns(st.session_state["campaigns_data"])


# -------------------------
# ADS MANAGEMENT
# -------------------------
elif page == "Ads Management":
    st.title("Madgicx MVP Dashboard – ⚙️ Ads Management")

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
    st.subheader("📦 Vytvořit nový Ad Set")

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

    st.markdown("---")
    st.subheader("🎨 Vytvořit Ad Creative (přes object_story_spec s image_url)")

    with st.form("create_creative_form"):
        account_id = st.text_input("Ad Account ID (bez 'act_')", key="creative_account")
        creative_name = st.text_input("Název Creativu", key="creative_name")
        page_id = st.text_input("Page ID", key="creative_page_id")
        message = st.text_area("Text reklamy", key="creative_message")
        image_url = st.text_input("Obrázek (URL)", key="creative_image")

        submit_creative = st.form_submit_button("Vytvořit Creative")

        if submit_creative:
            payload = {
                "account_id": account_id,
                "name": creative_name,
                "object_story_spec": {
                    "page_id": page_id,
                    "link_data": {
                        "message": message,
                        "link": "https://example.com",
                        "image_url": image_url
                    }
                }
            }
            res = requests.post("http://localhost:8000/create_creative", json=payload)
            if res.status_code == 200:
                st.success(f"Creative vytvořen: {res.json()}")
            else:
                st.error(f"Chyba: {res.text}")

    st.markdown("---")
    st.subheader("📢 Vytvořit Ad")

    with st.form("create_ad_form"):
        adset_id = st.text_input("Ad Set ID", key="ad_adset_id")
        ad_name = st.text_input("Název reklamy", key="ad_name")
        creative_id = st.text_input("Creative ID", key="ad_creative_id")
        status = st.selectbox("Stav", ["PAUSED", "ACTIVE"], key="ad_status")

        submit_ad = st.form_submit_button("Vytvořit Ad")

        if submit_ad:
            payload = {
                "adset_id": adset_id,
                "name": ad_name,
                "creative_id": creative_id,
                "status": status
            }
            res = requests.post("http://localhost:8000/create_ad", json=payload)
            if res.status_code == 200:
                st.success(f"Reklama vytvořena: {res.json()}")
            else:
                st.error(f"Chyba: {res.text}")

    st.markdown("---")
    st.subheader("🖼️ Upload obrázku pro reklamu")

    with st.form("upload_image_form"):
        account_id = st.text_input("Ad Account ID (bez 'act_')", key="upload_account")
        image_file = st.file_uploader("Vyber obrázek (JPG/PNG)", type=["jpg", "jpeg", "png"], key="upload_image")
        submit_upload = st.form_submit_button("Nahrát obrázek")

        if submit_upload and image_file is not None:
            files = {'file': (image_file.name, image_file.getvalue(), image_file.type)}
            data = {'account_id': account_id}
            res = requests.post("http://localhost:8000/upload_ad_image", files=files, data=data)
            if res.status_code == 200:
                images = res.json().get("images", {})
                if images:
                    image_hash = list(images.values())[0].get("hash", "Nezískán")
                    st.success(f"Nahráno. Hash: {image_hash}")
                else:
                    st.error(f"Chyba: Obrázek nebyl nahrán. Odpověď: {res.json()}")
                    image_hash = "Nezískán"
                st.success(f"Obrázek nahrán. Hash: `{image_hash}`")
            else:
                st.error(f"Chyba: {res.text}")

    st.markdown("---")
    st.subheader("🎨 Vytvořit Ad Creative (přes image_hash – link ad)")

    with st.form("create_adcreative_form"):
        account_id = st.text_input("Ad Account ID (bez 'act_')", key="adcreative_account")
        creative_name = st.text_input("Název Creativu", key="adcreative_name")
        title = st.text_input("Titulek reklamy", key="adcreative_title")
        body = st.text_area("Text reklamy", key="adcreative_body")
        object_url = st.text_input("Cílový odkaz (např. https://example.com)", key="adcreative_url")
        image_hash = st.text_input("Image Hash (z předchozího kroku)", key="adcreative_hash")

        submit_creative = st.form_submit_button("Vytvořit Ad Creative")

        if submit_creative:
            res = requests.post("http://localhost:8000/create_adcreative", json={
                "account_id": account_id,
                "name": creative_name,
                "title": title,
                "body": body,
                "object_url": object_url,
                "image_hash": image_hash
            })

            if res.status_code == 200:
                if "id" in res.json():
                    st.success(f"Creative vytvořen: ID {res.json()['id']}")
                else:
                    st.error("Chyba při vytváření Creativu:")
                    st.code(res.json(), language="json")
            else:
                st.error(f"Chyba: {res.text}")

# -------------------------
# ADS LIBRARY
# -------------------------
elif page == "Ads Library":
    st.title("Madgicx MVP Dashboard – 📚 Ads Library")
    st.info("Tato sekce bude zobrazovat uložené creatives, obrázky a archiv kampaní (TODO).")
