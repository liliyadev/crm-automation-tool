import streamlit as st
import pandas as pd
import plotly.express as px

# ─── 1) Page Setup ───
st.set_page_config(page_title="CRM Dashboard", layout="wide")
st.title("CRM Contact Automation Dashboard")

# ─── 2) Load & Score DataFrame ───
df = pd.read_csv("contacts.csv")
df["score"] = (
      df["engagement"] * 0.4
    + (df["revenue"] / df["revenue"].max() * 100) * 0.3
    + df["industry_fit"] * 0.3
).round(1)

# ─── 3) Top Metrics ───
col1, col2, col3 = st.columns(3)
col1.metric("Total Contacts", df.shape[0])
col2.metric("Average Lead Score", f"{df['score'].mean():.1f}")
col3.metric("Highest Engagement", f"{df['engagement'].max():.0f}%")
st.markdown("<br>", unsafe_allow_html=True)

# ─── 4) Initialize Session-State Defaults ───
if "min_score" not in st.session_state:
    st.session_state.min_score = int(df["score"].min())

if "revenue_range" not in st.session_state:
    st.session_state.revenue_range = (
        int(df["revenue"].min()),
        int(df["revenue"].max()),
    )

if "eng_threshold" not in st.session_state:
    st.session_state.eng_threshold = int(df["engagement"].min())

# ─── 5) Interactive Filters (one slider per key) ───
st.subheader("Filters")

min_score = st.slider(
    "Minimum Lead Score",
    int(df["score"].min()),
    int(df["score"].max()),
    key="min_score"               # reads/writes st.session_state.min_score
)

revenue_range = st.slider(
    "Revenue Range",
    int(df["revenue"].min()),
    int(df["revenue"].max()),
    value=st.session_state.revenue_range,
    key="revenue_range"
)

eng_threshold = st.slider(
    "Minimum Engagement (%)",
    int(df["engagement"].min()),
    int(df["engagement"].max()),
    value=st.session_state.eng_threshold,
    key="eng_threshold"
)

# ─── 6) Apply Filters ───
filtered_df = df[
    (df["score"] >= min_score)
  & (df["revenue"].between(*revenue_range))
  & (df["engagement"] >= eng_threshold)
]

st.markdown("<br>", unsafe_allow_html=True)

# ─── 7) Download Button ───
csv_bytes = filtered_df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="📥 Download Filtered Data as CSV",
    data=csv_bytes,
    file_name="scored_contacts.csv",
    mime="text/csv",
)

# ─── 8) Conditional Formatting ───
def highlight_by_score(row):
    s = row["score"]
    if s >= 80:
        color = "#D4EFDF"
    elif s >= 50:
        color = "#FCF3CF"
    else:
        color = "#FADBD8"
    return [f"background-color: {color}"] * len(row)

with st.expander("🔍 Show Detailed Contacts Table", expanded=False):
    styled = filtered_df.style.apply(highlight_by_score, axis=1)
    st.write(styled)

st.markdown("<br>", unsafe_allow_html=True)

# ─── 9) Charts ───
st.subheader("Top 10 Leads by Score")
top10 = filtered_df.nlargest(10, "score")
fig1 = px.bar(
    top10,
    x="name",
    y="score",
    color="score",
    color_continuous_scale="Blues",
    hover_data=["email", "industry_fit", "revenue", "engagement"]
)
st.plotly_chart(fig1, use_container_width=True)

st.subheader("Engagement vs. Revenue")
fig2 = px.scatter(
    filtered_df,
    x="engagement",
    y="revenue",
    size="industry_fit",
    hover_name="name",
    hover_data={
        "email": True,
        "score": True,
        "industry_fit": True,
        "engagement": ":.1f",
        "revenue": ":.0f"
    },
    labels={"industry_fit": "Fit Score"},
    height=450
)
st.plotly_chart(fig2, use_container_width=True)
