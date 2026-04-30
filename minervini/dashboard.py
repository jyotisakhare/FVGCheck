# dashboard_pro.py

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import time
from symbol_loader import load_market_symbols
from strategy import check_entry
from features import add_relative_strength
from config import CONFIG
from features import calculate_score

# ================= CONFIG =================
REFRESH_SECONDS = 60

MARKETS = {
    "US": ["AAPL", "MSFT", "NVDA", "TSLA", "AMZN"],
    "INDIA": ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS"]
}

INDEX_MAP = {
    "US": "^NDX",     # S&P 500
    "INDIA": "^NSEI"   # Nifty 50
}

# ================= DATA CLEANING =================
def clean_df(df):

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df = df[["Open", "High", "Low", "Close", "Volume"]].copy()

    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df.dropna(inplace=True)

    return df


# ================= INDICATORS =================
def add_indicators(df):

    df["EMA20"] = df["Close"].ewm(span=20).mean()
    df["EMA50"] = df["Close"].ewm(span=50).mean()
    df["SMA150"] = df["Close"].rolling(150).mean()

    df["52W_HIGH"] = df["Close"].rolling(252).max()
    df["VOL_AVG20"] = df["Volume"].rolling(20).mean()

    return df



# ================= STRATEGY =================
# def check_entry(df, market, config):
#
#     if len(df) < 200:
#         return False
#
#     row = df.iloc[-1]
#
#     required = ["Close", "EMA20", "EMA50", "SMA150", "VOL_AVG20"]
#
#     # ===== Safety checks =====
#     for col in required:
#         if col not in row or pd.isna(row[col]) or not np.isscalar(row[col]):
#             return False
#
#     # ===== RS FILTER =====
#     if "RS" not in df.columns or "RS_MA" not in df.columns:
#         return False
#
#     rs = df["RS"].iloc[-1]
#     rs_ma = df["RS_MA"].iloc[-1]
#
#     if pd.isna(rs) or pd.isna(rs_ma):
#         return False
#
#     # RS must be rising
#     if df["RS"].iloc[-1] < df["RS"].iloc[-5]:
#         return False
#
#     # ===== Trend structure =====
#     if not (
#         float(row["Close"]) >
#         float(row["EMA20"]) >
#         float(row["EMA50"]) >
#         float(row["SMA150"])
#     ):
#         return False
#
#     # ===== Breakout =====
#     prev_high = df["Close"].rolling(252).max().iloc[-2]
#
#     if row["Close"] < prev_high:
#         return False
#
#     # ===== Volume =====
#     vol_mult = 1.5 if market == "US" else 1.8
#
#     if row["Volume"] < vol_mult * row["VOL_AVG20"]:
#         return False
#
#     # ===== Breakout strength =====
#     candle_range = row["High"] - row["Low"]
#
#     if candle_range == 0:
#         return False
#
#     strength = (row["Close"] - row["Low"]) / candle_range
#
#     min_strength = 0.65 if market == "US" else 0.75
#
#     if strength < min_strength:
#         return False
#
#     # ===== Liquidity =====
#     liquidity = row["Close"] * row["Volume"]
#
#     if market == "US" and liquidity < 5e6:
#         return False
#
#     if market == "INDIA" and liquidity < 2e7:
#         return False
#
#     return True

# ================= FETCH STOCK =================
@st.cache_data(ttl=30000)
def fetch_stock(symbol):

    try:
        df = yf.download(symbol, period="2y", interval="1d", progress=False)

        if df.empty:
            return None

        df = clean_df(df)
        df = add_indicators(df)

        return df

    except:
        return None


# ================= FETCH INDEX =================
@st.cache_data(ttl=30000)
def fetch_index(symbol):

    df = yf.download(symbol, period="1y", interval="1d", progress=False)

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df = df[["Close"]].copy()
    df["EMA50"] = df["Close"].ewm(span=50).mean()
    df["EMA200"] = df["Close"].ewm(span=200).mean()

    df.dropna(inplace=True)

    return df


# ================= MARKET FILTER =================
def is_market_strong(index_df):

    if len(index_df) < 200:
        return False

    row = index_df.iloc[-1]

    if pd.isna(row["Close"]) or pd.isna(row["EMA50"]):
        return False

    return row["Close"] > row["EMA50"] > row["EMA200"]



# ================= UI =================
st.set_page_config(layout="wide")
st.title("🚀 Momentum Scanner PRO")

markets = load_market_symbols("")

selected_market = st.selectbox(
    "Select Market",
    list(markets.keys())
)

symbols = markets[selected_market]

if len(symbols) == 0:
    st.warning(f"No symbols found for {selected_market}")
    st.stop()

st.write(f"Loaded {len(symbols)} symbols from {selected_market}")

# ===== INDEX FILTER =====
index_symbol = INDEX_MAP[selected_market]
index_df = fetch_index(index_symbol)

market_ok = is_market_strong(index_df)

if market_ok:
    st.success(f"✅ Market is STRONG ({index_symbol})")
else:
    st.success(f"❌ Market is WEAK ({index_symbol}) — No trades allowed")
    # st.stop()

# ===== SCAN =====
candidates = []
cfg = CONFIG.copy()
cfg["MARKET"] = selected_market

for symbol in symbols:

    df = fetch_stock(symbol)

    if df is None:
        continue

    df = add_relative_strength(df, index_df)

    i = len(df) - 1
    # print(f"checking {symbol}")
    if check_entry(df, i, cfg, debug=True):
        score = calculate_score(df, i)
        candidates.append({
            "Symbol": symbol,
            "Score": score,
            "Price": float(df["Close"].iloc[-1]),
            "Volume": int(df["Volume"].iloc[-1]),
            "RS": round(df["RS"].iloc[-1], 3)
        })

TOP_N = 10

df_final = pd.DataFrame()

if candidates:
    df_candidates = pd.DataFrame(candidates)
    df_candidates = df_candidates.sort_values(by="Score", ascending=False)
    df_final = df_candidates.head(TOP_N)

# ===== DISPLAY =====
if not df_final.empty:
    st.success(f"Top {TOP_N} Elite Setups")
    st.dataframe(df_final, use_container_width=True)
else:
    st.warning("No elite setups today")




# ===== AUTO REFRESH =====
st.caption(f"Auto refresh every {REFRESH_SECONDS}s")
time.sleep(REFRESH_SECONDS)
st.rerun()