import pandas as pd
import yfinance as yf
import os
import streamlit as st

def load_market_symbols(base_path=""):
    market_files = {
        "US": "nasdaq.csv",
        "INDIA": "nifty500.csv",
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

        return df
    except e:
        print(f"fetch_symbol failed for {e}")
        return None