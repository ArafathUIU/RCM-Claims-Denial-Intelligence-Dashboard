"""RCM Claims Denial Intelligence - Streamlit Dashboard.

Multi-page interactive web dashboard for analyzing
healthcare claim denial trends and revenue recovery.
"""
import streamlit as st
import pandas as pd
import os

st.set_page_config(
    page_title="RCM Denial Intelligence",
    page_icon=":hospital:",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data
def load_data():
    """Load claims data from CSV with caching."""
    data_path = os.path.join(
        os.path.dirname(__file__), "..", "data", "claims_data.csv"
    )
    df = pd.read_csv(data_path)
    df["service_date"] = pd.to_datetime(df["service_date"])
    df["billing_date"] = pd.to_datetime(df["billing_date"])
    df["denial_date"] = pd.to_datetime(df["denial_date"], errors="coerce")
    df["recovery_date"] = pd.to_datetime(df["recovery_date"], errors="coerce")
    df["payment_date"] = pd.to_datetime(df["payment_date"], errors="coerce")
    return df


df = load_data()

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
