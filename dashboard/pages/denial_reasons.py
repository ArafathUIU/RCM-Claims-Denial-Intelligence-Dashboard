"""Denial Reasons page - Top denial codes, financial impact, treemap."""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from data_loader import load_claims_data

df = load_claims_data()
denied = df[df["claim_status"] != "Paid"]

st.title("Denial Reason Analysis")
st.markdown("_Top denial codes by frequency and financial impact_")

reason_stats = denied.groupby("reason_code").agg(
    count=("claim_id", "count"),
    total_denied=("denied_amount", "sum"),
    avg_aging=("aging_days", "mean"),
).reset_index()
reason_stats = reason_stats.sort_values("total_denied", ascending=False)
reason_stats["pct"] = reason_stats["total_denied"] / reason_stats["total_denied"].sum() * 100

col1, col2 = st.columns(2)

with col1:
    fig1 = px.bar(
        reason_stats.head(10), x="reason_code", y="count",
        title="Top 10 Denial Reasons by Count",
        labels={"reason_code": "", "count": "Claims"},
        color="count", color_continuous_scale="Blues",
    )
    fig1.update_layout(height=400)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    fig2 = px.treemap(
        reason_stats, path=["reason_code"], values="total_denied",
        title="Denied Amount by Reason (Treemap)",
        color="total_denied", color_continuous_scale="Reds",
    )
    fig2.update_layout(height=400)
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

reason_stats["cumulative"] = reason_stats["total_denied"].cumsum()
reason_stats["cum_pct"] = reason_stats["cumulative"] / reason_stats["total_denied"].sum() * 100

fig3 = go.Figure()
fig3.add_trace(go.Bar(
    name="Denied Amount", x=reason_stats["reason_code"],
    y=reason_stats["total_denied"], marker_color="#2E75B6",
))
fig3.add_trace(go.Scatter(
    name="Cumulative %", x=reason_stats["reason_code"],
    y=reason_stats["cum_pct"], yaxis="y2",
    mode="lines+markers", line=dict(color="#C00000", width=3),
    marker=dict(size=8),
))
fig3.update_layout(
    title="Pareto Chart — Denial Reasons (Denied $ + Cumulative %)",
    yaxis=dict(title="Denied Amount ($)"),
    yaxis2=dict(title="Cumulative %", overlaying="y", side="right", range=[0, 105]),
    height=450,
)
st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")
st.subheader("Denial Reasons by Payer")

selected_payer = st.selectbox(
    "Select Payer", options=sorted(df["payer_name"].unique()), index=0
)

payer_reasons = denied[denied["payer_name"] == selected_payer].groupby(
    "reason_code"
).agg(
    count=("claim_id", "count"),
    denied_amt=("denied_amount", "sum"),
).reset_index()
payer_reasons = payer_reasons.sort_values("denied_amt", ascending=False)

fig4 = px.bar(
    payer_reasons.head(10), x="reason_code", y="denied_amt",
    title=f"Top Denial Reasons — {selected_payer}",
    labels={"reason_code": "", "denied_amt": "Denied Amount ($)"},
    color="denied_amt", color_continuous_scale="Oranges",
)
fig4.update_layout(height=400)
st.plotly_chart(fig4, use_container_width=True)
