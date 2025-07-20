# frontend/utils.py
import streamlit as st
import pandas as pd

def display_campaigns(data):
    if "data" in data:
        df = pd.DataFrame(data["data"])
        st.dataframe(df)
    else:
        st.warning("Žádná data nebyla načtena.")
