import streamlit as st
import pandas as pd
import time

from config import CONFIG
from symbol_loader import fetch_symbol
from portfolio import Portfolio

# ================= CONFIG =================
DATA_PATH = "data"
POSITIONS_FILE = "minervini/ravi_positions_ind.csv"
REFRESH = 300

st.set_page_config(layout="wide")
st.title("🚀 Live Pro Dashboard")

# ================= MARKET =================
market = st.selectbox("Market", ["US", "INDIA"])
CONFIG["MARKET"] = market


# =========================================================
# 📁 SECTION 1 — LIVE PORTFOLIO
# =========================================================
st.header("📁 Live Portfolio "+market)

if market == "INDIA":
    POSITIONS_FILE = "minervini/ravi_positions_ind.csv"
else:
    POSITIONS_FILE = "minervini/ravi_positions_us.csv"

try:
    positions_df = pd.read_csv(POSITIONS_FILE)
    positions_df["Entry Date"] = pd.to_datetime(positions_df["Entry Date"], dayfirst=True)

    portfolio = Portfolio(CONFIG["INITIAL_CAPITAL"], CONFIG)

    # load positions
    for _, r in positions_df.iterrows():
        portfolio.positions[r["Symbol"]] = {
            "entry": r["Entry Price"],
            "shares": r["Shares"],
            "highest": r["Highest"],
            "partial": r["Partial"],
            "stop": r["Stop"],
            "entry_date": r["Entry Date"],
        }

    results = []

    for symbol, pos in portfolio.positions.items():
        print(f"checking live  {symbol}")
        df = fetch_symbol(symbol)

        if df is None:
            print(f"no live data {symbol}")
            continue

        row = df.iloc[-1]
        i = len(df) - 1

        # update highest
        pos["highest"] = max(pos["highest"], row["Close"])

        # ===== EXIT LOGIC =====
        exit_reason = None

        if row["Close"] < pos["stop"]:
            exit_reason = "HARD STOP"

        try:
            entry_idx = df.index.get_loc(pos["entry_date"])
            days = i - entry_idx
        except:
            days = 0

        if not exit_reason and CONFIG["MARKET"] == "INDIA":
            if 3 <= days <= 5 and row["Close"] < 0.97 * pos["entry"]:
                exit_reason = "FAILED BREAKOUT"

        # 🔥 REUSE CORE LOGIC
        exit_flag, exit_reason = portfolio.check_exit(symbol, row, i, CONFIG, df)

        action = "EXIT" if exit_flag else "HOLD"

        # next stop
        if pos["partial"]:
            next_stop = CONFIG["TRAIL_AFTER_PARTIAL"] * pos["highest"]
        else:
            next_stop = CONFIG["TRAIL_INITIAL"] * pos["highest"]

        pnl = (row["Close"] - pos["entry"]) / pos["entry"] * 100

        results.append({
            "Symbol": symbol,
            "Price": round(row["Close"], 2),
            "PnL %": round(pnl, 2),
            "Highest": round(pos["highest"], 2),
            "Next Stop": round(next_stop, 2),
            "Action": action,
            "Reason": exit_reason if exit_reason else "",
            "Days": days
        })

    results.sort(key=lambda x: x['PnL %'], reverse=True)
    df_live = pd.DataFrame(results)

    st.dataframe(df_live, use_container_width=True)

    exits = df_live[df_live["Action"] == "EXIT"]

    if not exits.empty:
        st.error("🚨 Exit Signals")
        st.dataframe(exits)

except Exception as e:
    print(e)
    st.warning(f"Portfolio error: {e}")


# =========================================================
# 🧠 SECTION 3 — RISK OVERVIEW
# =========================================================
st.header("🧠 Risk Overview")

if 'df_live' in locals() and not df_live.empty:

    total_positions = len(df_live)
    exit_count = len(df_live[df_live["Action"] == "EXIT"])

    st.metric("Total Positions", total_positions)
    st.metric("Exit Signals", exit_count)

else:
    st.info("No active positions")


# =========================================================
# 🔄 AUTO REFRESH
# =========================================================
st.caption(f"Auto refresh every {REFRESH} seconds")

time.sleep(REFRESH)
st.rerun()