import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import json
import os

# GOOGLE SHEETS AUTH
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds_json = json.loads(os.environ["GOOGLE_CREDENTIALS"])

creds = Credentials.from_service_account_info(
    creds_json,
    scopes=SCOPES
)

client = gspread.authorize(creds)

sheet = client.open_by_key(
    "1qVvlUiLqyh93LsfdFHFwKLEMUra3qlrDIMSbqNhTVV8"
).sheet1

st.set_page_config(page_title="Tracking Dashboard", layout="wide")

st.title("📦 Live Tracking Dashboard")

# LOAD DATA
data = sheet.get_all_records()
df = pd.DataFrame(data)

if df.empty:
    st.warning("No data found")
    st.stop()

# CLEAN STATUS COLUMN
df["Status"] = df["Status"].fillna("Unknown")

# =========================
# METRICS
# =========================
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Orders", len(df))
col2.metric("RTO", len(df[df["Status"] == "RTO"]))
col3.metric("Out for Delivery", len(df[df["Status"] == "Out for Delivery"]))
col4.metric("Delivered", len(df[df["Status"] == "Delivered"]))

st.divider()

# =========================
# FILTERS
# =========================
status_filter = st.selectbox(
    "Filter Status",
    ["All", "RTO", "Out for Delivery", "Delivered", "Unknown"]
)

if status_filter != "All":
    df = df[df["Status"] == status_filter]

# =========================
# LIVE TABLE
# =========================
st.dataframe(df, use_container_width=True)

# =========================
# AUTO REFRESH
# =========================
st.caption("Auto-refresh every 30 seconds")
st.rerun()
