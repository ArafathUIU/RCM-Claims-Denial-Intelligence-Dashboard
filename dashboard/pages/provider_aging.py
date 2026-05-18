"""Provider & Aging page - Provider drill-down and AR aging analysis."""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from data_loader import load_claims_data

df = load_claims_data()

st.title("Provider & Aging Analysis")
st.markdown("_Provider performance and accounts receivable aging_")

tab1, tab2 = st.tabs(["Provider Performance", "AR Aging"])

with tab1:
    departments = sorted(df["department"].unique())
    selected_dept = st.selectbox("Select Department", options=["All"] + departments, index=0)

    if selected_dept == "All":
        provider_df = df
    else:
        provider_df = df[df["department"] == selected_dept]

    provider_stats = provider_df.groupby(["provider_name", "department"]).agg(
        total=("claim_id", "count"),
        denied=("claim_status", lambda x: (x != "Paid").sum()),
        denied_amt=("denied_amount", "sum"),
        recovered_amt=("recovered_amount", "sum"),
        avg_aging=("aging_days", "mean"),
    ).reset_index()
    provider_stats["denial_rate"] = provider_stats["denied"] / provider_stats["total"] * 100
    provider_stats["recovery_rate"] = (
        provider_stats["recovered_amt"] / provider_stats["denied_amt"].replace(0, None) * 100
    ).fillna(0)
    provider_stats = provider_stats.sort_values("denial_rate", ascending=False)

    fig1 = px.bar(
        provider_stats.head(15), x="provider_name", y="denial_rate",
        title="Top Providers by Denial Rate",
        labels={"provider_name": "", "denial_rate": "Denial Rate %"},
        color="denial_rate", color_continuous_scale="Reds",
        hover_data=["department", "total", "denied_amt"],
    )
    fig1.update_layout(height=450)
    st.plotly_chart(fig1, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        dept_stats = df.groupby("department").agg(
            total=("claim_id", "count"),
            denied=("claim_status", lambda x: (x != "Paid").sum()),
        ).reset_index()
        dept_stats["denial_rate"] = dept_stats["denied"] / dept_stats["total"] * 100
        dept_stats = dept_stats.sort_values("denial_rate", ascending=False)

        fig2 = px.bar(
            dept_stats, y="department", x="denial_rate",
            title="Denial Rate by Department",
            labels={"department": "", "denial_rate": "Denial Rate %"},
            color="denial_rate", color_continuous_scale="Blues",
            orientation="h",
        )
        fig2.update_layout(height=400)
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        provider_payer = provider_df.groupby(["provider_name", "payer_name"]).agg(
            denied_amt=("denied_amount", "sum"),
        ).reset_index()
        top_providers = provider_stats.head(5)["provider_name"].tolist()
        heatmap_df = provider_payer[provider_payer["provider_name"].isin(top_providers)]
        pivot = heatmap_df.pivot(
            index="provider_name", columns="payer_name", values="denied_amt"
        ).fillna(0)

        fig3 = px.imshow(
            pivot, text_auto=".2s",
            title="Top 5 Providers — Denied $ by Payer",
            labels={"x": "Payer", "y": "Provider", "color": "Denied $"},
            color_continuous_scale="Reds",
        )
        fig3.update_layout(height=400)
        st.plotly_chart(fig3, use_container_width=True)
