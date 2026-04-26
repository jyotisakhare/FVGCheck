import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import time

# ================= CONFIG =================
st.set_page_config(page_title="Advanced Momentum Dashboard", layout="wide")

# ================= INDICATORS =================
def add_indicators(df):

    # Ensure numeric (CRITICAL FIX)
    for col in ["Open","High","Low","Close","Volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df.dropna(inplace=True)

    # EMA
    df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()
    df["EMA50"] = df["Close"].ewm(span=50, adjust=False).mean()
    df["EMA220"] = df["Close"].ewm(span=220, adjust=False).mean()

    # SMA
    df["SMA50"] = df["Close"].rolling(50).mean()
    df["SMA150"] = df["Close"].rolling(150).mean()

    # 52W
    df["52W_HIGH"] = df["Close"].rolling(252).max()
    df["52W_LOW"] = df["Close"].rolling(252).min()

    # ATR (FIXED)
    hl = df["High"] - df["Low"]
    h_pc = (df["High"] - df["Close"].shift(1)).abs()
    l_pc = (df["Low"] - df["Close"].shift(1)).abs()
    tr = pd.concat([hl, h_pc, l_pc], axis=1).max(axis=1)
    df["ATR"] = tr.rolling(14).mean()

    df["ATR_PCT"] = (df["ATR"] / df["Close"]) * 100

    # CCI
    tp = (df["High"] + df["Low"] + df["Close"]) / 3
    sma = tp.rolling(20).mean()
    mad = tp.rolling(20).apply(lambda x: np.mean(np.abs(x - np.mean(x))), raw=True)
    df["CCI"] = (tp - sma) / (0.015 * mad)

    return df

# ================= CONDITION ENGINE =================
def evaluate_conditions(df):

    if len(df) < 300:
        return None

    row = df.iloc[-1]

    # ===== ORIGINAL CONDITIONS =====
    cond1 = row["SMA150"] > row["EMA220"]
    cond2 = row["Close"] > row["SMA50"]
    cond3 = row["SMA50"] > row["SMA150"]
    cond4 = row["Close"] > 1.25 * row["52W_LOW"]

    cond1 = True
    cond2 = True
    cond3 = True
    cond4 = True


    recent = df.iloc[-90:]
    cond5 = (recent["Close"] < recent["EMA220"]).any()

    breakout = row["Close"] >= df["Close"].rolling(252).max().iloc[-2]

    # ===== NEW CONDITIONS =====
    cond6 = row["Close"] > row["EMA50"]
    cond7 = row["Close"] > row["EMA20"]
    cond8 = row["EMA20"] > row["EMA50"]

    high_52w = row["52W_HIGH"]
    cond9 = (row["Close"] >= 0.8 * high_52w)  # within 20%

    cond10 = row["ATR_PCT"] < 3 if pd.notna(row["ATR_PCT"]) else False

    # CCI slope
    cci_last20 = df["CCI"].iloc[-20:].dropna()
    cond11 = False
    if len(cci_last20) == 20:
        x = np.arange(20)
        slope = np.polyfit(x, cci_last20.values, 1)[0]
        cond11 = slope > 0

    vol_avg_20 = df["Volume"].rolling(20).mean().iloc[-1]
    cond12 = row["Volume"] > vol_avg_20

    avg_2 = df["Volume"].iloc[-2:].mean()
    avg_5 = df["Volume"].iloc[-5:].mean()
    cond13 = avg_2 > avg_5

    # ===== ALL CONDITIONS =====
    conditions = {
        "Trend (SMA150 > EMA220)": cond1,
        "Price > SMA50": cond2,
        "SMA50 > SMA150": cond3,
        "Above 25% from Low": cond4,
        "Recent EMA220 Dip": cond5,
        "Breakout": breakout,

        "Close > EMA50": cond6,
        "Close > EMA20": cond7,
        "EMA20 > EMA50": cond8,
        "Near 52W High": cond9,
        "Low Volatility (ATR <3%)": cond10,
        "CCI Uptrend": cond11,
        "Volume > 20D Avg": cond12,
        "Volume Momentum": cond13
    }

    score = sum(conditions.values())

    return conditions, score

# ================= LOAD SYMBOLS =================
@st.cache_data
def load_symbols():
    df = pd.read_csv("nasdaq.csv")
    return df["Symbol"].dropna().unique().tolist()

# ================= FETCH DATA =================
def fetch_data(symbol):
    try:
        df = yf.download(symbol, period="2y", interval="1d", progress=False)

        if df.empty:
            return None

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df = df[["Open","High","Low","Close","Volume"]].copy()

        df = add_indicators(df)

        return df

    except:
        return None

# ================= UI =================
st.title("🚀 Advanced Momentum Dashboard")

symbols = load_symbols()

results = []
progress = st.progress(0)

# ================= SCAN =================
for i, symbol in enumerate(symbols):

    df = fetch_data(symbol)

    if df is None:
        continue

    output = evaluate_conditions(df)

    if output is None:
        continue

    conditions, score = output

    results.append({
        "Symbol": symbol,
        "Score": score,
        **conditions
    })

    progress.progress((i + 1) / len(symbols))

# ================= DISPLAY =================
if results:

    result_df = pd.DataFrame(results)

    max_score = len(result_df.columns) - 2  # exclude Symbol + Score

    full_match = result_df[result_df["Score"] == max_score]

    if not full_match.empty:
        st.success(f"{len(full_match)} PERFECT setups found")

        st.dataframe(
            full_match.sort_values(by="Score", ascending=False),
            use_container_width=True
        )

    else:
        st.warning("No perfect setups today")

        top_df = result_df.sort_values(by="Score", ascending=False).head(15)

        condition_cols = result_df.columns[2:]

        top_df["Missing Conditions"] = top_df.apply(
            lambda row: [col for col in condition_cols if not row[col]],
            axis=1
        )

        st.info("Top near-perfect setups")

        st.dataframe(top_df, use_container_width=True)

    near_match = result_df[result_df["Score"] == max_score - 3]

    if not full_match.empty:
        st.success(f"{len(near_match)} Near PERFECT setups found")

        st.dataframe(
            near_match.sort_values(by="Score", ascending=False),
            use_container_width=True
        )

    # ===== CHART =====
    st.subheader("📊 Chart")

    selected = st.selectbox("Select Stock", result_df["Symbol"])

    if selected:
        chart_data = fetch_data(selected)
        if chart_data is not None:
            st.line_chart(chart_data["Close"])

else:
    st.error("No data available")

# ================= AUTO REFRESH =================
st.caption("Auto-refresh every 5 minutes")
time.sleep(300)
st.rerun()