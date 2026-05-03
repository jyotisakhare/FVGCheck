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

    score = 0
    details = {}

    # ===== CORE =====
    breakout = row["Close"] >= df["Close"].rolling(252).max().iloc[-2]
    if breakout:
        score += 25
    details["Breakout"] = breakout

    high_52w = row["52W_HIGH"]
    near_high = row["Close"] >= 0.8 * high_52w
    if near_high:
        score += 15
    details["Near 52W High"] = near_high

    ema_align = row["EMA20"] > row["EMA50"]
    if ema_align:
        score += 15
    details["EMA20 > EMA50"] = ema_align

    vol_avg_20 = df["Volume"].rolling(20).mean().iloc[-1]
    vol_strong = row["Volume"] > vol_avg_20
    if vol_strong:
        score += 15
    details["Volume > Avg"] = vol_strong

    # ===== MEDIUM =====
    if row["Close"] > row["EMA20"]:
        score += 5
        details["Close > EMA20"] = True
    else:
        details["Close > EMA20"] = False

    if row["Close"] > row["EMA50"]:
        score += 5
        details["Close > EMA50"] = True
    else:
        details["Close > EMA50"] = False

    if row["SMA50"] > row["SMA150"]:
        score += 5
        details["SMA50 > SMA150"] = True
    else:
        details["SMA50 > SMA150"] = False

    if row["Close"] > 1.25 * row["52W_LOW"]:
        score += 5
        details["Above 25% Low"] = True
    else:
        details["Above 25% Low"] = False

    # CCI slope
    cci_last20 = df["CCI"].iloc[-20:].dropna()
    cci_up = False
    if len(cci_last20) == 20:
        x = np.arange(20)
        slope = np.polyfit(x, cci_last20.values, 1)[0]
        if slope > 0:
            score += 5
            cci_up = True
    details["CCI Uptrend"] = cci_up

    # ===== LOW IMPACT =====
    if row["SMA150"] > row["EMA220"]:
        score += 2
        details["Trend"] = True
    else:
        details["Trend"] = False

    if row["Close"] > row["SMA50"]:
        score += 2
        details["Price > SMA50"] = True
    else:
        details["Price > SMA50"] = False

    avg_2 = df["Volume"].iloc[-2:].mean()
    avg_5 = df["Volume"].iloc[-5:].mean()
    vol_mom = avg_2 > avg_5
    if vol_mom:
        score += 3
    details["Volume Momentum"] = vol_mom

    if pd.notna(row["ATR_PCT"]) and row["ATR_PCT"] < 3:
        score += 3
        details["Low ATR"] = True
    else:
        details["Low ATR"] = False

    return details, score

#========Display Results
def display_results(results):
    if results:

        result_df = pd.DataFrame(results)

        max_score = len(result_df.columns) - 2  # exclude Symbol + Score

        # Define thresholds
        HIGH_QUALITY = 70
        MEDIUM_QUALITY = 55

        top_df = result_df.sort_values(by="Score", ascending=False)

        high_df = top_df[top_df["Score"] >= HIGH_QUALITY]
        mid_df = top_df[(top_df["Score"] >= MEDIUM_QUALITY) & (top_df["Score"] < HIGH_QUALITY)]

        if not high_df.empty:
            st.success(f"🔥 High Quality Setups (Score ≥ {HIGH_QUALITY})")
            st.dataframe(high_df.head(10), use_container_width=True)

        if not mid_df.empty:
            st.warning(f"⚡ Medium Setups (Score ≥ {MEDIUM_QUALITY})")
            st.dataframe(mid_df.head(10), use_container_width=True)

        if high_df.empty and mid_df.empty:
            st.info("No strong setups — showing best available")

            fallback = top_df.head(10)

            condition_cols = result_df.columns[2:]

            fallback["Missing Conditions"] = fallback.apply(
                lambda row: [col for col in condition_cols if not row[col]],
                axis=1
            )

            st.dataframe(fallback, use_container_width=True)

# ================= LOAD SYMBOLS =================
@st.cache_data(ttl=14400)
def load_symbols(filename):
    df = pd.read_csv(filename)
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
st.title("🚀 Advanced Momentum Dashboard India")

symbols = load_symbols("nifty500.csv")

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

# ================= UI =================
st.title("🚀 Advanced Momentum Dashboard US")

symbolsUS = load_symbols("nasdaq.csv")

resultsUS = []
progressUS = st.progress(0)

# ================= SCAN =================
for i, symbol in enumerate(symbolsUS):

    df = fetch_data(symbol)

    if df is None:
        continue

    output = evaluate_conditions(df)

    if output is None:
        continue

    conditions, score = output

    resultsUS.append({
        "Symbol": symbol,
        "Score": score,
        **conditions
    })

    progressUS.progress((i + 1) / len(symbolsUS))

# ================= DISPLAY =================
display_results(results)
display_results(resultsUS)


# ================= AUTO REFRESH =================
st.caption("Auto-refresh every 1 hr")
time.sleep(3600)
st.rerun()