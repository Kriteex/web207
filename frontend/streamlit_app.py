# frontend/streamlit_app.py
import streamlit as st
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from scripts.ingest_data import load_campaigns
from frontend.utils import display_campaigns

st.title("Madgicx MVP Dashboard")

if st.button("Načíst kampaně"):
    data = load_campaigns()
    display_campaigns(data)
