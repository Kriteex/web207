# frontend/utils.py
import streamlit as st
import pandas as pd

def display_campaigns(data):
    total_spend = 0
    total_revenue = 0
    roas_values = []

    for account in data:
        st.subheader(f"Účet: {account['account_id']}")
        for campaign in account["campaigns"]:
            spend = campaign.get("spend", 0)
            revenue = campaign.get("revenue", 0)
            roas = revenue / spend if spend > 0 else 0

            total_spend += spend
            total_revenue += revenue
            roas_values.append(roas)

            with st.expander(f"🎯 Kampaň: {campaign['name']} | ROAS: {roas:.2f}"):
                st.write(f"ID: {campaign['id']}, Cíl: {campaign.get('objective', '')}")
                st.write(f"Spend: ${spend:.2f}, Revenue: ${revenue:.2f}, ROAS: {roas:.2f}")
                for adset in campaign.get("adsets", []):
                    with st.expander(f"📦 Adset: {adset['name']}"):
                        st.write(f"ID: {adset['id']}")
                        for ad in adset.get("ads", []):
                            st.markdown(f"🪧 Reklama: **{ad['name']}** (ID: `{ad['id']}`)")

    if total_spend > 0:
        blended_roas = total_revenue / total_spend
        st.markdown("---")
        st.subheader("📈 Monthly Goals")
        st.progress(min(total_revenue / 100000, 1.0), text=f"Revenue: ${total_revenue:.0f} / $100,000")
        st.progress(min(total_spend / 50000, 1.0), text=f"Spend: ${total_spend:.0f} / $50,000")
        st.success(f"Blended ROAS: {blended_roas:.2f} vs Goal 2.0")