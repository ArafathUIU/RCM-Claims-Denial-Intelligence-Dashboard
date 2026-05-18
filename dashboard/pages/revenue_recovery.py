"""Revenue Recovery page - Appeal funnel, recovery rates, waterfall."""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from data_loader import load_claims_data

df = load_claims_data()
denied = df[df["claim_status"] != "Paid"]

st.title("Revenue Recovery Analysis")
st.markdown("_Track appeals, recovered revenue, and recovery efficiency_")

num_denied = len(denied)
num_appeals = denied["appeal_flag"].sum()
num_wins = len(df[df["claim_status"] == "Recovered"])
num_losses = len(df[df["claim_status"] == "Written Off"])
denied_amt = denied["denied_amount"].sum()
recovered_amt = df[df["claim_status"] == "Recovered"]["recovered_amount"].sum()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Denied Claims", f"{num_denied:,}")
col2.metric("Appeals Filed", f"{num_appeals:,}", f"{num_appeals/num_denied*100:.1f}%")
col3.metric("Appeals Won", f"{num_wins:,}", f"{num_wins/num_appeals*100:.1f}%" if num_appeals else "0%")
col4.metric("Recovery Rate ($)", f"{recovered_amt/denied_amt*100:.1f}%" if denied_amt else "0%")

st.markdown("---")

funnel = go.Figure(go.Funnel(
    y=["Denied", "Appealed", "Recovered", "Written Off"],
    x=[num_denied, num_appeals, num_wins, num_losses],
    textposition="inside",
    textinfo="value+percent total",
    marker=dict(color=["#2E75B6", "#ED7D31", "#006100", "#C00000"]),
))
funnel.update_layout(title="Appeal Funnel — From Denial to Recovery", height=400)
st.plotly_chart(funnel, use_container_width=True)

col_a, col_b = st.columns(2)

with col_a:
    recovery_by_reason = denied.groupby("reason_code").agg(
        denied_amt=("denied_amount", "sum"),
        recovered_amt=("recovered_amount", "sum"),
    ).reset_index()
    recovery_by_reason["recovery_rate"] = (
        recovery_by_reason["recovered_amt"] / recovery_by_reason["denied_amt"].replace(0, None) * 100
    )
    recovery_by_reason = recovery_by_reason.sort_values("recovery_rate", ascending=False)

    fig1 = px.bar(
        recovery_by_reason.head(10), x="reason_code", y="recovery_rate",
        title="Recovery Rate by Denial Reason (Top 10)",
        labels={"reason_code": "", "recovery_rate": "Recovery %"},
        color="recovery_rate", color_continuous_scale="Greens",
    )
    fig1.update_layout(height=400)
    st.plotly_chart(fig1, use_container_width=True)

with col_b:
    recovery_data = [
        ("Billed", df["billed_amount"].sum()),
        ("Allowed", df["allowed_amount"].sum()),
        ("Denied", denied_amt),
        ("Recovered", recovered_amt),
        ("Written Off", denied_amt - recovered_amt),
    ]
    labels, values = zip(*recovery_data)

    fig2 = go.Figure(go.Waterfall(
        name="Revenue",
        orientation="v",
        measure=["absolute", "relative", "relative", "relative", "relative"],
        x=labels, y=values,
        connector={"line": {"color": "rgb(63, 63, 63)"}},
        decreasing={"marker": {"color": "#C00000"}},
        increasing={"marker": {"color": "#006100"}},
        totals={"marker": {"color": "#2E75B6"}},
    ))
    fig2.update_layout(title="Revenue Flow Waterfall", height=400)
    st.plotly_chart(fig2, use_container_width=True)
