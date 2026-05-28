import streamlit as st
import pandas as pd
import time
import io

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

from config import CONFIG
from symbol_loader import fetch_symbol
from portfolio import Portfolio

# =========================================================
# CONFIG
# =========================================================
REFRESH = 300

# GOOGLE DRIVE FILE IDS
INDIA_FILE_ID = "150IbwjtX9yRJHfZqMBUNfTG-Nu2w5LKc"
US_FILE_ID = "1rvdZ6glWzJompV70--pnKwXN2OmlDFsF"

# =========================================================
# GOOGLE DRIVE CONNECTION
# =========================================================
@st.cache_resource
def connect_drive():

    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=["https://www.googleapis.com/auth/drive"]
    )

    service = build(
        "drive",
        "v3",
        credentials=credentials
    )

    return service


drive_service = connect_drive()

# =========================================================
# READ CSV FROM GOOGLE DRIVE
# =========================================================
def read_csv_from_drive(file_id):

    request = drive_service.files().get_media(
        fileId=file_id
    )

    file_data = io.BytesIO()

    downloader = MediaIoBaseDownload(
        file_data,
        request
    )

    done = False

    while not done:
        status, done = downloader.next_chunk()

    file_data.seek(0)

    df = pd.read_csv(file_data)

    return df

# =========================================================
# STREAMLIT PAGE
# =========================================================
st.set_page_config(layout="wide")

st.title("🚀 Live Pro Dashboard")

# =========================================================
# MARKET
# =========================================================
market = st.selectbox(
    "Market",
    ["US", "INDIA"]
)

CONFIG["MARKET"] = market

# =========================================================
# SELECT FILE
# =========================================================
if market == "INDIA":
    FILE_ID = INDIA_FILE_ID
else:
    FILE_ID = US_FILE_ID

# =========================================================
# LIVE PORTFOLIO
# =========================================================
st.header(f"📁 Live Portfolio {market}")

try:

    # =====================================================
    # READ CSV
    # =====================================================
    positions_df = read_csv_from_drive(FILE_ID)

    positions_df["Entry Date"] = pd.to_datetime(
        positions_df["Entry Date"],
        dayfirst=True
    )

    portfolio = Portfolio(
        CONFIG["INITIAL_CAPITAL"],
        CONFIG
    )

    # =====================================================
    # LOAD POSITIONS
    # =====================================================
    for _, r in positions_df.iterrows():

        portfolio.positions[r["Symbol"]] = {
            "entry": r["Entry Price"],
            "shares": r["Shares"],
            "highest": r["Highest"],
            "partial": r["Partial"],
            "stop": r["Stop"],
            "entry_date": r["Entry Date"],
            "recommended_by": r["Recom By"],
        }

    results = []
    results_trade_team = []

    # =====================================================
    # ANALYZE POSITIONS
    # =====================================================
    for symbol, pos in portfolio.positions.items():

        print(f"checking live {symbol}")

        df = fetch_symbol(symbol)

        if df is None:
            continue

        row = df.iloc[-1]

        i = len(df) - 1

        # update highest
        pos["highest"] = max(
            pos["highest"],
            row["Close"]
        )

        exit_reason = None

        if row["Close"] < pos["stop"]:
            exit_reason = "HARD STOP"

        try:

            entry_idx = df.index.get_loc(
                pos["entry_date"]
            )

            days = i - entry_idx

        except:
            days = 0

        # failed breakout
        if (
            not exit_reason
            and CONFIG["MARKET"] == "INDIA"
        ):

            if (
                3 <= days <= 5
                and row["Close"] < 0.97 * pos["entry"]
            ):

                exit_reason = "FAILED BREAKOUT"

        # core exit logic
        exit_flag, exit_reason = portfolio.check_exit(
            symbol,
            row,
            i,
            CONFIG,
            df
        )

        action = "EXIT" if exit_flag else "HOLD"

        # next stop
        if pos["partial"]:
            next_stop = CONFIG["TRAIL_AFTER_PARTIAL"] * pos["highest"]
        else:
            next_stop = CONFIG["TRAIL_INITIAL"] * pos["highest"]

        pnl = (
            (row["Close"] - pos["entry"])
            / pos["entry"]
        ) * 100

        data = {
            "Symbol": symbol,
            "Price": round(row["Close"], 2),
            "PnL %": round(pnl, 2),
            "Partial": pos["partial"],
            "Shares": pos["shares"],
            "Action": action,
            # "Highest": round(pos["highest"], 2),
            "Next Stop": round(next_stop, 2),
            "Reason": exit_reason if exit_reason else "",
            "Days": days
        }

        if pos["recommended_by"] == "Trade team":

            results_trade_team.append(data)

        else:

            data["By"] = pos["recommended_by"]

            results.append(data)

    # =====================================================
    # DISPLAY
    # =====================================================
    results.sort(
        key=lambda x: x["PnL %"],
        reverse=True
    )

    results_trade_team.sort(
        key=lambda x: x["PnL %"],
        reverse=True
    )

    df_live = pd.DataFrame(results)

    df_live_trade_team = pd.DataFrame(
        results_trade_team
    )

    st.dataframe(
        df_live,
        use_container_width=True
    )

    st.dataframe(
        df_live_trade_team,
        use_container_width=True
    )

    exits = df_live[
        df_live["Action"] == "EXIT"
    ]

    if not exits.empty:

        st.error("🚨 Exit Signals")

        st.dataframe(exits)

except Exception as e:

    st.warning(f"Portfolio error: {e}")

# =========================================================
# RISK OVERVIEW
# =========================================================
st.header("🧠 Risk Overview")

if 'df_live' in locals() and not df_live.empty:

    total_positions = (
        len(df_live)
        + len(df_live_trade_team)
    )

    exit_count = len(
        df_live[df_live["Action"] == "EXIT"]
    )

    if not df_live_trade_team.empty:

        exit_count += len(
            df_live_trade_team[
                df_live_trade_team["Action"] == "EXIT"
            ]
        )

    st.metric(
        "Total Positions",
        total_positions
    )

    st.metric(
        "Exit Signals",
        exit_count
    )

else:

    st.info("No active positions")

# =========================================================
# AUTO REFRESH
# =========================================================
st.caption(
    f"Auto refresh every {REFRESH} seconds"
)

time.sleep(REFRESH)

st.rerun()