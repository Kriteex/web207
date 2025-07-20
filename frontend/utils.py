# frontend/utils.py
import streamlit as st
import pandas as pd

def display_campaigns(data):
    for account in data:
        st.subheader(f"Účet: {account['account_id']}")
        for campaign in account["campaigns"]:
            with st.expander(f"🎯 Kampaň: {campaign['name']}"):
                st.write(f"ID: {campaign['id']}, Cíl: {campaign.get('objective', '')}")
                for adset in campaign.get("adsets", []):
                    with st.expander(f"📦 Adset: {adset['name']}"):
                        st.write(f"ID: {adset['id']}")
                        for ad in adset.get("ads", []):
                            st.markdown(f"🪧 Reklama: **{ad['name']}** (ID: `{ad['id']}`)")