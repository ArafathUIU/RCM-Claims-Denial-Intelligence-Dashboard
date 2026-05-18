"""Shared data loading utilities for dashboard pages."""
import pandas as pd
import streamlit as st
import os


@st.cache_data
def load_claims_data():
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
