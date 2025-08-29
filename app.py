import streamlit as st
import pandas as pd
import plotly.express as px

# ─── 0) Page Config & Custom CSS ────────────────────────────────────────────────
st.set_page_config(page_title="CRM Dashboard", layout="wide")

st.markdown(
    """
    <style>
    /* Hide Streamlit footer & menu */
    #MainMenu, footer { visibility: hidden; }

    /* Page background */
    [data-testid="stAppViewContainer"] { background-color: #eef5f9; }

    /* Header */
    header {
      background: linear-gradient(90deg, #0077b6 0%, #00b4d8 100%);
      color: #ffffff !important;
      padding: 1rem 2rem;
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      font-weight: 600;
      margin-bottom: 1rem;
      box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }

    /* Sidebar card */
    [data-testid="stSidebar"] .block-container {
      background: #ffffff;
      border-radius: 10px;
      padding: 1.5rem;
      box-shadow: 2px 2px 12px rgba(0,0,0,0.05);
    }

    /* Metric cards */
    .stMetric > div {
      background: #ffffff !important;
      border-left: 5px solid #00b4d8 !important;
      border-radius: 8px !important;
      padding: 1rem !important;
      font-family: 'Segoe UI', sans-serif;
      box-shadow: 0 2px 6px rgba(0,0,0,0.05) !important;
    }

    /* Buttons */
    .stDownloadButton>button,
    .stButton>button {
      background-color: #0077b6 !important;
      color: #ffffff !important;
      border-radius: 4px !important;
      padding: .6rem 1.2rem !important;
      font-weight: 500;
    }
    .stDownloadButton>button:hover,
    .stButton>button:hover {
      background-color: #005f87 !important;
    }

    /* DataFrame styling */
    .dataframe th {
      background-color: #0096c7;
      color: white;
      font-weight: 600;
      padding: 0.5rem;
    }
    .dataframe td {
      padding: 0.5rem;
      border: 1px solid #ddd;
    }
    .dataframe tr:nth-child(even) {
      background: #f0f8ff;
    }
    .dataframe tr:hover {
      background: #caf0f8 !important;
    }

    /* Expander header */
    .stExpander>div:first-child {
      background-color: #ade8f4 !important;
      border-radius: 6px !important;
      font-weight: 500;
    }

    /* Plotly charts container */
    [data-testid="stPlotlyChart"] {
      background: #ffffff;
      border-radius: 8px;
      padding: 1rem;
      box-shadow: 0 2px 8px rgba(0,0,0,0.05);
      margin-bottom: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─── 1) Title ───────────────────────────────────────────────────────────────────
st.title("CRM Contact Automation Dashboard")

# ─── 2) Load & Score ────────────────────────────────────────────────────────────
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

# ─── 4) Session-State Defaults ─────────────────────────────────────────────────
if "min_score" not in st.session_state:
    st.session_state.min_score = int(df["score"].min())
if "revenue_range" not in st.session_state:
    st.session_state.revenue_range = (int(df["revenue"].min()), int(df["revenue"].max()))
if "eng_threshold" not in st.session_state:
    st.session_state.eng_threshold = int(df["engagement"].min())

# ─── 5) Filters ─────────────────────────────────────────────────────────────────
st.subheader("Filters")
min_score = st.slider("Minimum Lead Score",
                      int(df["score"].min()),
                      int(df["score"].max()),
                      key="min_score")
revenue_range = st.slider("Revenue Range",
                          int(df["revenue"].min()),
                          int(df["revenue"].max()),
                          key="revenue_range")
eng_threshold = st.slider("Minimum Engagement (%)",
                          int(df["engagement"].min()),
                          int(df["engagement"].max()),
                          key="eng_threshold")

# ─── 6) Apply Filters ───────────────────────────────────────────────────────────
filtered_df = df[
    (df["score"] >= min_score) &
    (df["revenue"].between(*revenue_range)) &
    (df["engagement"] >= eng_threshold)
]

st.markdown("<br>", unsafe_allow_html=True)

# ─── 7) Download ─────────────────────────────────────────────────────────────────
csv_bytes = filtered_df.to_csv(index=False).encode("utf-8")
st.download_button("📥 Download Filtered Data as CSV",
                   csv_bytes, "scored_contacts.csv", "text/csv")

# ─── 8) Styled Table ────────────────────────────────────────────────────────────
def highlight_by_score(row):
    if row.score >= 80:
        return ["background-color: #caf0f8"] * len(row)
    elif row.score >= 50:
        return ["background-color: #ade8f4"] * len(row)
    else:
        return ["background-color: #90e0ef"] * len(row)

with st.expander("🔍 Show Detailed Contacts Table"):
    styled = filtered_df.style\
        .apply(highlight_by_score, axis=1)\
        .set_table_styles([
            {"selector": "th", "props": [("font-size", "1rem")]},
            {"selector": "td", "props": [("font-size", "0.9rem")]}
        ])
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
    color_continuous_scale=px.colors.sequential.Tealgrn,
    template="plotly_white",
)
fig1.update_traces(marker_line_color="white", marker_line_width=1)
fig1.update_layout(
    title_font_family="Segoe UI",
    title_font_size=18,
    font_family="Segoe UI",
    font_color="#023047",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=40, r=40, t=60, b=40),
)
st.plotly_chart(fig1, use_container_width=True)

st.subheader("Engagement vs. Revenue")
fig2 = px.scatter(
    filtered_df,
    x="engagement",
    y="revenue",
    size="industry_fit",
    color="score",
    color_continuous_scale=px.colors.sequential.Tealgrn,
    template="plotly_white",
    hover_name="name",
)
fig2.update_traces(marker=dict(line=dict(width=1, color="#023047"), opacity=0.8))
fig2.update_layout(
    font_family="Segoe UI",
    font_color="#023047",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=40, r=40, t=60, b=40),
)
st.plotly_chart(fig2, use_container_width=True)
