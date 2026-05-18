"""Overview page - Executive summary with KPI cards and trend charts."""
import streamlit as st
import plotly.express as px
from data_loader import load_claims_data

df = load_claims_data()

st.title("RCM Denial Intelligence Dashboard")
st.markdown("_Healthcare Insurance Claim Denial Analytics — Jan 2024 to Dec 2025_")

with st.expander("Filters", expanded=False):
    c1, c2 = st.columns(2)
    with c1:
        date_range = st.date_input(
            "Date Range",
            value=(df["service_date"].min(), df["service_date"].max()),
            min_value=df["service_date"].min().date(),
            max_value=df["service_date"].max().date(),
        )
    with c2:
        payer_types = st.multiselect(
            "Payer Type",
            options=sorted(df["payer_type"].unique()),
            default=sorted(df["payer_type"].unique()),
        )

if len(date_range) == 2:
    mask = (df["service_date"] >= pd.Timestamp(date_range[0])) & \
           (df["service_date"] <= pd.Timestamp(date_range[1]))
    mask &= df["payer_type"].isin(payer_types)
    filtered_df = df[mask]
else:
    filtered_df = df

st.markdown("---")

total_claims = len(filtered_df)
denied_df = filtered_df[filtered_df["claim_status"] != "Paid"]
denied_count = len(denied_df)
denial_rate = denied_count / total_claims * 100
total_denied = denied_df["denied_amount"].sum()
total_recovered = df[df["claim_status"] == "Recovered"]["recovered_amount"].sum()
recovery_rate = total_recovered / total_denied * 100 if total_denied else 0
appealed = denied_df[denied_df["appeal_flag"] == 1]
appeal_win_rate = len(df[df["claim_status"] == "Recovered"]) / len(appealed) * 100 if len(appealed) > 0 else 0
avg_aging = denied_df["aging_days"].mean()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Claims", f"{total_claims:,}")
col2.metric("Denial Rate", f"{denial_rate:.1f}%")
col3.metric("Total Denied", f"${total_denied:,.0f}")
col4.metric("Recovery Rate", f"{recovery_rate:.1f}%")

col5, col6, col7, col8 = st.columns(4)
col5.metric("Claims Denied", f"{denied_count:,}")
col6.metric("Appeal Win Rate", f"{appeal_win_rate:.1f}%")
col7.metric("Total Recovered", f"${total_recovered:,.0f}")
col8.metric("Avg Aging Days", f"{avg_aging:.0f}")

st.markdown("---")

monthly = filtered_df.groupby(filtered_df["service_date"].dt.to_period("M")).agg(
    total=("claim_id", "count"),
    denied=("claim_status", lambda x: (x != "Paid").sum()),
    denied_amt=("denied_amount", "sum"),
    recovered_amt=("recovered_amount", "sum"),
).reset_index()
monthly["service_date"] = monthly["service_date"].astype(str)
monthly["denial_rate"] = monthly["denied"] / monthly["total"] * 100

fig = px.line(
    monthly, x="service_date", y="denial_rate",
    title="Monthly Denial Rate Trend",
    labels={"service_date": "Month", "denial_rate": "Denial Rate %"},
)
fig.update_traces(line=dict(color="#2E75B6", width=3))
fig.update_layout(height=400)

st.plotly_chart(fig, use_container_width=True)

col_a, col_b = st.columns(2)

with col_a:
    fig2 = px.bar(
        monthly, x="service_date", y="denied_amt",
        title="Monthly Denied Amount ($)",
        labels={"service_date": "Month", "denied_amt": "Denied $"},
    )
    fig2.update_traces(marker_color="#C00000")
    fig2.update_layout(height=350)
    st.plotly_chart(fig2, use_container_width=True)

with col_b:
    fig3 = px.bar(
        monthly, x="service_date", y="recovered_amt",
        title="Monthly Recovered Amount ($)",
        labels={"service_date": "Month", "recovered_amt": "Recovered $"},
    )
    fig3.update_traces(marker_color="#006100")
    fig3.update_layout(height=350)
    st.plotly_chart(fig3, use_container_width=True)
