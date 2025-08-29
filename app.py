import streamlit as st
import pandas as pd
import plotly.express as px

# ─── Custom CSS Injection ──────────────────────────────────────────────────────
def inject_css():
    st.markdown(
        """
        <style>
        /* Hide default Streamlit menu & footer */
        #MainMenu { visibility: hidden; }
        footer { visibility: hidden; }

        /* Page background */
        [data-testid="stAppViewContainer"] {
            background-color: #f5f7fa;
        }

        /* Header styling */
        header {
            background-color: #ffffff;
            padding: 16px 0;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            margin-bottom: 1rem;
        }

        /* Sidebar container */
        [data-testid="stSidebar"] .block-container {
            background-color: #ffffff;
            border-radius: 8px;
            padding: 1.5rem;
            box-shadow: 2px 2px 12px rgba(0,0,0,0.05);
        }

        /* Main content area padding */
        [data-testid="stAppViewContainer"] .main {
            padding: 1rem 2rem;
        }

        /* Metric cards */
        .stMetric > div {
            background-color: #ffffff !important;
            border-radius: 8px !important;
            padding: 1rem !important;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05) !important;
        }

        /* Buttons (Download & default st.button) */
        .stDownloadButton>button,
        .stButton>button {
            background-color: #0052cc !important;
            color: #ffffff !important;
            border: none !important;
            padding: .6rem 1.2rem !important;
            border-radius: 4px !important;
            font-weight: 500;
        }
        .stDownloadButton>button:hover,
        .stButton>button:hover {
            background-color: #003d99 !important;
        }

        /* Expander header */
        .stExpander>div:first-child {
            background-color: #e7f3ff !important;
            border-radius: 6px !important;
        }

        /* Chart containers */
        [data-testid="stPlotlyChart"] {
            background-color: #ffffff;
            border-radius: 8px;
            padding: 1rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            margin-bottom: 1rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

inject_css()
# ────────────────────────────────────────────────────────────────────────────────

# ─── 1) Page Setup ─────────────────────────────────────────────────────────────
st.set_page_config(page_title="CRM Dashboard", layout="wide")
st.title("CRM Contact Automation Dashboard")

# ─── 2) Load & Score DataFrame ─────────────────────────────────────────────────
df = pd.read_csv("contacts.csv")
df["score"] = (
      df["engagement"] * 0.4
    + (df["revenue"] / df["revenue"].max() * 100) * 0.3
    + df["industry_fit"] * 0.3
).round(1)

# ─── 3) Top Metrics ─────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)
col1.metric("Total Contacts", df.shape[0])
col2.metric("Average Lead Score", f"{df['score'].mean():.1f}")
col3.metric("Highest Engagement", f"{df['engagement'].max():.0f}%")
st.markdown("<br>", unsafe_allow_html=True)

# ─── 4) Initialize Session-State Defaults ──────────────────────────────────────
if "min_score" not in st.session_state:
    st.session_state.min_score = int(df["score"].min())

if "revenue_range" not in st.session_state:
    st.session_state.revenue_range = (
        int(df["revenue"].min()),
        int(df["revenue"].max()),
    )

if "eng_threshold" not in st.session_state:
    st.session_state.eng_threshold = int(df["engagement"].min())

# ─── 5) Interactive Filters ────────────────────────────────────────────────────
st.subheader("Filters")

min_score = st.slider(
    "Minimum Lead Score",
    int(df["score"].min()),
    int(df["score"].max()),
    key="min_score"
)

revenue_range = st.slider(
    "Revenue Range",
    int(df["revenue"].min()),
    int(df["revenue"].max()),
    key="revenue_range"
)

eng_threshold = st.slider(
    "Minimum Engagement (%)",
    int(df["engagement"].min()),
    int(df["engagement"].max()),
    key="eng_threshold"
)

# ─── 6) Apply Filters ───────────────────────────────────────────────────────────
filtered_df = df[
    (df["score"] >= min_score)
  & (df["revenue"].between(*revenue_range))
  & (df["engagement"] >= eng_threshold)
]

st.markdown("<br>", unsafe_allow_html=True)

# ─── 7) Download Button ─────────────────────────────────────────────────────────
csv_bytes = filtered_df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="📥 Download Filtered Data as CSV",
    data=csv_bytes,
    file_name="scored_contacts.csv",
    mime="text/csv",
)

# ─── 8) Conditional Formatting & Table ──────────────────────────────────────────
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

# ─── 9) Charts ─────────────────────────────────────────────────────────────────
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
