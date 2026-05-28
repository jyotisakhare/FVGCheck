import streamlit as st
import pandas as pd
import time

from config import CONFIG
from create_new_position import trade_entry_widget
from sheetutils import connect_google_sheets, read_sheet
from symbol_loader import fetch_symbol
from portfolio import Portfolio

# =========================================================
# CONFIG
# =========================================================
REFRESH = 300

# GOOGLE SHEET NAMES
INDIA_SHEET = "positions"
US_SHEET = "positions_us"

# =========================================================
# GOOGLE SHEETS CONNECTION
# =========================================================

gs_client = connect_google_sheets()

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
    ["US", "INDIA"],
    key="market_select1"
)

CONFIG["MARKET"] = market

# =========================================================
# SELECT SHEET
# =========================================================
if market == "INDIA":
    SHEET_NAME = INDIA_SHEET
else:
    SHEET_NAME = US_SHEET

# =========================================================
# LIVE PORTFOLIO
# =========================================================
st.header(f"📁 Live Portfolio {market}")

try:

    # =====================================================
    # READ GOOGLE SHEET
    # =====================================================
    positions_df = read_sheet(SHEET_NAME, gs_client)

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

        # =================================================
        # UPDATE HIGHEST
        # =================================================
        pos["highest"] = max(
            pos["highest"],
            row["Close"]
        )

        # =================================================
        # EXIT LOGIC
        # =================================================
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

        # =================================================
        # FAILED BREAKOUT
        # =================================================
        if (
            not exit_reason
            and CONFIG["MARKET"] == "INDIA"
        ):

            if (
                3 <= days <= 5
                and row["Close"] < 0.97 * pos["entry"]
            ):

                exit_reason = "FAILED BREAKOUT"

        # =================================================
        # CORE EXIT LOGIC
        # =================================================
        exit_flag, exit_reason = portfolio.check_exit(
            symbol,
            row,
            i,
            CONFIG,
            df
        )

        action = "EXIT" if exit_flag else "HOLD"

        # =================================================
        # NEXT STOP
        # =================================================
        if pos["partial"]:

            next_stop = (
                CONFIG["TRAIL_AFTER_PARTIAL"]
                * pos["highest"]
            )

        else:

            next_stop = (
                CONFIG["TRAIL_INITIAL"]
                * pos["highest"]
            )

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
            "Highest": round(pos["highest"], 2),
            "Next Stop": round(next_stop, 2),
            "Reason": exit_reason if exit_reason else "",
            "Days": days
        }

        # =================================================
        # SPLIT TRADE TEAM
        # =================================================
        if pos["recommended_by"] == "Trade team":

            results_trade_team.append(data)

        else:

            data["By"] = pos["recommended_by"]

            results.append(data)

    # =====================================================
    # SORT RESULTS
    # =====================================================
    results.sort(
        key=lambda x: x["PnL %"],
        reverse=True
    )

    results_trade_team.sort(
        key=lambda x: x["PnL %"],
        reverse=True
    )

    # =====================================================
    # DATAFRAMES
    # =====================================================
    df_live = pd.DataFrame(results)

    df_live_trade_team = pd.DataFrame(
        results_trade_team
    )

    # =====================================================
    # DISPLAY
    # =====================================================
    st.dataframe(
        df_live,
        use_container_width=True
    )

    st.dataframe(
        df_live_trade_team,
        use_container_width=True
    )

    # =====================================================
    # EXIT SIGNALS
    # =====================================================
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

if st.button("Add entry"):
    trade_entry_widget(market)

# =========================================================
# AUTO REFRESH
# =========================================================
st.caption(
    f"Auto refresh every {REFRESH} seconds"
)

time.sleep(REFRESH)

st.rerun()