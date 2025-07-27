# frontend/utils.py
"""
Small utilities used by the Streamlit UI.
Behavior parity with original display_campaigns implementation.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List

import streamlit as st


def _safe_roas(revenue: float, spend: float) -> float:
    """Return ROAS or 0 when spend is 0 (preserves original logic)."""
    return (revenue / spend) if spend > 0 else 0.0


def display_campaigns(data: List[Dict[str, Any]]) -> None:
    """
    Render campaigns tree and a simple goals section below it.

    Expected input shape:
    [
      {
        "account_id": "...",
        "campaigns": [
          {
            "id": "...", "name": "...", "objective": "...",
            "spend": <float>, "revenue": <float>,  # may be absent depending on backend param
            "adsets": [
              {"id": "...", "name": "...", "ads": [{"id": "...", "name": "..."}, ...]},
              ...
            ]
          }, ...
        ]
      }, ...
    ]
    """
    total_spend = 0.0
    total_revenue = 0.0
    roas_values: List[float] = []

    for account in data:
        st.subheader(f"Účet: {account['account_id']}")
        for campaign in account["campaigns"]:
            spend = float(campaign.get("spend", 0) or 0.0)
            revenue = float(campaign.get("revenue", 0) or 0.0)
            roas = _safe_roas(revenue, spend)

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
