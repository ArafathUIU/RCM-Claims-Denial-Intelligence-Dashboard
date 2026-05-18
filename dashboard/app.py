"""RCM Claims Denial Intelligence - Streamlit Dashboard.

Multi-page interactive web dashboard for analyzing
healthcare claim denial trends and revenue recovery.
"""
import streamlit as st
from data_loader import load_claims_data

st.set_page_config(
    page_title="RCM Denial Intelligence",
    page_icon=":hospital:",
    layout="wide",
    initial_sidebar_state="expanded",
)

df = load_claims_data()

st.sidebar.title("RCM Denial Intelligence")
st.sidebar.markdown("---")
st.sidebar.markdown(
    f"**{len(df):,}** claims loaded  \n"
    f"**{df['provider_name'].nunique()}** providers  \n"
    f"**{df['payer_name'].nunique()}** payers  \n"
    f"Jan 2024 – Dec 2025"
)

st.sidebar.markdown("---")
st.sidebar.caption("Phase 4 — Streamlit Dashboard")
