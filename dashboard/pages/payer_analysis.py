"""Payer Analysis page - Denial rate and financial performance by payer."""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from data_loader import load_claims_data

df = load_claims_data()

st.title("Payer Performance Analysis")
st.markdown("_Denial rates, denied amounts, and recovery rates by insurance payer_")

payers = sorted(df["payer_name"].unique())
selected_payers = st.multiselect(
    "Select Payers", options=payers, default=payers[:6]
)

filtered = df[df["payer_name"].isin(selected_payers)]

payer_stats = filtered.groupby("payer_name").agg(
    total=("claim_id", "count"),
    denied=("claim_status", lambda x: (x != "Paid").sum()),
    denied_amt=("denied_amount", "sum"),
    recovered_amt=("recovered_amount", "sum"),
).reset_index()
payer_stats["denial_rate"] = payer_stats["denied"] / payer_stats["total"] * 100
payer_stats["recovery_rate"] = (
    payer_stats["recovered_amt"] / payer_stats["denied_amt"].replace(0, None) * 100
).fillna(0)
payer_stats = payer_stats.sort_values("denial_rate", ascending=False)

col1, col2 = st.columns(2)

with col1:
    fig1 = px.bar(
        payer_stats, x="payer_name", y="denial_rate",
        title="Denial Rate % by Payer",
        labels={"payer_name": "", "denial_rate": "Denial Rate %"},
        color="denial_rate", color_continuous_scale="Reds",
    )
    fig1.update_layout(height=400)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    fig2 = px.bar(
        payer_stats, x="payer_name", y="denied_amt",
        title="Total Denied Amount by Payer ($)",
        labels={"payer_name": "", "denied_amt": "Denied $"},
        color="denied_amt", color_continuous_scale="Oranges",
    )
    fig2.update_layout(height=400)
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")
st.subheader("Payer Comparison Table")
st.dataframe(
    payer_stats.style
    .format({"denial_rate": "{:.1f}%", "recovery_rate": "{:.1f}%",
             "denied_amt": "${:,.0f}", "recovered_amt": "${:,.0f}",
             "total": "{:,}", "denied": "{:,}"})
    .background_gradient(subset=["denial_rate"], cmap="Reds")
    .background_gradient(subset=["recovery_rate"], cmap="Greens"),
    use_container_width=True,
    hide_index=True,
)
