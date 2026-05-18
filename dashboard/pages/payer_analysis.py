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

st.markdown("---")
st.subheader("Recovery & Appeal Performance")

payer_recovery = filtered.groupby("payer_name").agg(
    denied=("claim_status", lambda x: (x != "Paid").sum()),
    appeals=("appeal_flag", "sum"),
    wins=("claim_status", lambda x: (x == "Recovered").sum()),
    denied_amt=("denied_amount", "sum"),
    recovered_amt=("recovered_amount", "sum"),
).reset_index()
payer_recovery["appeal_rate"] = payer_recovery["appeals"] / payer_recovery["denied"] * 100
payer_recovery["appeal_success"] = payer_recovery["wins"] / payer_recovery["appeals"].replace(0, None) * 100
payer_recovery["recovery_rate"] = (
    payer_recovery["recovered_amt"] / payer_recovery["denied_amt"].replace(0, None) * 100
)

col3, col4 = st.columns(2)

with col3:
    fig3 = px.bar(
        payer_recovery, x="payer_name", y="recovery_rate",
        title="Recovery Rate % by Payer",
        labels={"payer_name": "", "recovery_rate": "Recovery %"},
        color="recovery_rate", color_continuous_scale="Greens",
    )
    fig3.update_layout(height=400)
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    fig4 = go.Figure()
    fig4.add_trace(go.Bar(
        name="Appeal Rate", x=payer_recovery["payer_name"],
        y=payer_recovery["appeal_rate"], marker_color="#2E75B6",
    ))
    fig4.add_trace(go.Bar(
        name="Success Rate", x=payer_recovery["payer_name"],
        y=payer_recovery["appeal_success"], marker_color="#ED7D31",
    ))
    fig4.update_layout(
        title="Appeal Rate vs Success Rate by Payer",
        barmode="group", height=400,
    )
    st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")

payer_type_stats = filtered.groupby("payer_type").agg(
    total=("claim_id", "count"),
    denied=("claim_status", lambda x: (x != "Paid").sum()),
    denied_amt=("denied_amount", "sum"),
    recovered_amt=("recovered_amount", "sum"),
    avg_aging=("aging_days", "mean"),
).reset_index()
payer_type_stats["denial_rate"] = payer_type_stats["denied"] / payer_type_stats["total"] * 100
payer_type_stats["recovery_rate"] = (
    payer_type_stats["recovered_amt"] / payer_type_stats["denied_amt"].replace(0, None) * 100
)

st.subheader("Payer Type Comparison")
pt_cols = st.columns(3)
for i, (_, row) in enumerate(payer_type_stats.iterrows()):
    with pt_cols[i]:
        bg = "#2E75B6" if row["payer_type"] == "Commercial" else \
             "#C00000" if row["payer_type"] == "Government" else "#ED7D31"
        st.markdown(
            f"<div style='background:{bg}; padding:15px; border-radius:10px; color:white'>"
            f"<h3>{row['payer_type']}</h3>"
            f"<p>Denial Rate: <b>{row['denial_rate']:.1f}%</b></p>"
            f"<p>Recovery Rate: <b>{row['recovery_rate']:.1f}%</b></p>"
            f"<p>Avg Aging: <b>{row['avg_aging']:.0f} days</b></p>"
            f"</div>",
            unsafe_allow_html=True,
        )
