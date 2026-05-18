"""Provider & Aging page - Provider drill-down and AR aging analysis."""
import streamlit as st
import pandas as pd
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

with tab2:
    denied_df = df[df["claim_status"] != "Paid"].copy()
    denied_df["aging_bucket"] = pd.cut(
        denied_df["aging_days"],
        bins=[0, 30, 60, 90, float("inf")],
        labels=["0-30 days", "31-60 days", "61-90 days", "90+ days"],
    )

    aging = denied_df.groupby("aging_bucket", observed=False).agg(
        count=("claim_id", "count"),
        denied_amt=("denied_amount", "sum"),
        recovered_amt=("recovered_amount", "sum"),
        avg_aging=("aging_days", "mean"),
    ).reset_index()
    aging["outstanding"] = aging["denied_amt"] - aging["recovered_amt"]
    aging["pct"] = aging["denied_amt"] / aging["denied_amt"].sum() * 100

    aging_order = ["0-30 days", "31-60 days", "61-90 days", "90+ days"]
    aging["_sort"] = aging["aging_bucket"].apply(lambda x: aging_order.index(x) if x in aging_order else 99)
    aging = aging.sort_values("_sort")

    col3, col4 = st.columns(2)

    with col3:
        bucket_colors = ["#006100", "#70AD47", "#ED7D31", "#C00000"]
        fig4 = go.Figure()
        fig4.add_trace(go.Bar(
            x=aging["aging_bucket"], y=aging["count"],
            marker_color=bucket_colors[:len(aging)],
            name="Claims",
        ))
        fig4.update_layout(
            title="Denied Claims by Aging Bucket",
            height=400, yaxis_title="Number of Claims",
        )
        st.plotly_chart(fig4, use_container_width=True)

    with col4:
        fig5 = px.pie(
            aging, names="aging_bucket", values="denied_amt",
            title="Denied $ Distribution by Aging Bucket",
            color="aging_bucket",
            color_discrete_map={
                "0-30 days": "#006100", "31-60 days": "#70AD47",
                "61-90 days": "#ED7D31", "90+ days": "#C00000",
            },
        )
        fig5.update_layout(height=400)
        st.plotly_chart(fig5, use_container_width=True)

    st.markdown("---")
    st.subheader("Aging by Payer & Department")

    aging_by_payer = denied_df.groupby("payer_name").agg(
        avg_aging=("aging_days", "mean"),
    ).reset_index()
    aging_by_payer = aging_by_payer.sort_values("avg_aging", ascending=False)

    col5, col6 = st.columns(2)

    with col5:
        fig6 = px.bar(
            aging_by_payer, x="payer_name", y="avg_aging",
            title="Average Aging Days by Payer",
            labels={"payer_name": "", "avg_aging": "Avg Days"},
            color="avg_aging", color_continuous_scale="Oranges",
        )
        fig6.update_layout(height=400)
        st.plotly_chart(fig6, use_container_width=True)

    with col6:
        aging_by_dept = denied_df.groupby("department").agg(
            avg_aging=("aging_days", "mean"),
        ).reset_index()
        aging_by_dept = aging_by_dept.sort_values("avg_aging", ascending=False)

        fig7 = px.bar(
            aging_by_dept, y="department", x="avg_aging",
            title="Average Aging Days by Department",
            labels={"department": "", "avg_aging": "Avg Days"},
            color="avg_aging", color_continuous_scale="Blues",
            orientation="h",
        )
        fig7.update_layout(height=400)
        st.plotly_chart(fig7, use_container_width=True)
