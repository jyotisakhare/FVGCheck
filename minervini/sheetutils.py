# =========================================================
# GOOGLE SHEETS CONNECTION
# =========================================================
import streamlit as st
import pandas as pd
import gspread
import time

from google.oauth2.service_account import Credentials

from config import CONFIG
from symbol_loader import fetch_symbol
from portfolio import Portfolio


@st.cache_resource
def connect_google_sheets():

    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    credentials = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scope
    )

    client = gspread.authorize(credentials)

    return client

# =========================================================
# READ GOOGLE SHEET
# =========================================================
def read_sheet(sheet_name, gs_client):

    sheet = gs_client.open(sheet_name).sheet1

    data = sheet.get_all_records()

    df = pd.DataFrame(data)

    return df
