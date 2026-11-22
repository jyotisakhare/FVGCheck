import numpy as np
import pandas as pd
import yfinance as yf
import os
import streamlit as st

def load_market_symbols(base_path=""):
    market_files = {
        "INDIA": "nifty500.csv",
        "US": "nasdaq.csv"
    }

    markets = {}

    for market, file in market_files.items():
        path = os.path.join(base_path, file)

        if not os.path.exists(path):
            print(f"⚠️ Missing file: {file}")
            markets[market] = []
            continue

        try:
            df = pd.read_csv(path)

            df.columns = [c.strip().lower() for c in df.columns]

            if "symbol" not in df.columns:
                raise ValueError(f"{file} must contain 'Symbol' column")

            symbols = (
                df["symbol"]
                .dropna()
                .astype(str)
                .str.strip()
                .unique()
                .tolist()
            )

            markets[market] = symbols

        except Exception as e:
            print(f"❌ Error loading {file}: {e}")
            markets[market] = []

    return markets

def load_market_symbols_from_file(filename):
    path = os.path.join(filename)

    if not os.path.exists(path):
        print(f"⚠️ Missing file: {filename}")
        return []
    print(f"⚠️ Loading file: {filename} {path}")
    try:
        df = pd.read_csv(path)
        df.columns = [c.strip().lower() for c in df.columns]

        if "symbol" not in df.columns:
            raise ValueError(f"{filename} must contain 'Symbol' column")

        symbols = (
            df["symbol"]
            .dropna()
            .astype(str)
            .str.strip()
            .unique()
            .tolist()
        )
        return symbols
    except Exception as e:
        print(f"❌ Error loading {filename}: {e}")

    return []

@st.cache_data(ttl=1500)
def fetch_symbol(symbol):
    try:
        df = yf.download(symbol, period="1y", interval="1d", progress=False)

        if df.empty:
            print(f"fetch_symbol failed for {symbol}")
            return None

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df = df[["Open", "High", "Low", "Close", "Volume"]].copy()
        df = df.apply(pd.to_numeric, errors="coerce")
        df.dropna(inplace=True)

        # indicators
        df["EMA10"] = df["Close"].ewm(span=10).mean()
        df["EMA20"] = df["Close"].ewm(span=20).mean()
        df["EMA50"] = df["Close"].ewm(span=50).mean()
        df["SMA150"] = df["Close"].rolling(150).mean()
        df_temp = df.copy()
        weekly_close = df_temp["Close"].resample("W-FRI").last()
        weekly_sma20 = weekly_close.rolling(window=20).mean()

        # Reindex / map back to daily dataframe and forward fill
        df["Weekly_SMA20"] = weekly_sma20.reindex(df.index, method="ffill")
        return df
    except e:
        print(f"fetch_symbol failed for {e}")
        return None

def chande_momentum_oscillator(close: pd.Series, period: int = 10) -> float:
    # Only the last (period + 1) prices are needed for the latest CMO value
    recent = np.asarray(close[-(period + 1):], dtype=float)
    if len(recent) < period + 1:
        raise ValueError(f"Need at least {period + 1} prices, got {len(recent)}")

    diff = np.diff(recent)
    sum_up = diff[diff > 0].sum()
    sum_down = -diff[diff < 0].sum()

    total = sum_up + sum_down
    return 0.0 if total == 0 else round(float(100.0 * (sum_up - sum_down) / total),0)