# frontend/streamlit_app.py
import streamlit as st
from scripts.ingest_data import load_campaigns
from frontend.utils import display_campaigns

st.title("Madgicx MVP Dashboard")

if st.button("Načíst kampaně"):
    data = load_campaigns()
    display_campaigns(data)
