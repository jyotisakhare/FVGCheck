# data.py

import pandas as pd
import numpy as np
import os
import yfinance as yf

from features import add_relative_strength


# ================= INDEX LOADER =================
def load_index_data(symbol="^GSPC"):  # Change to ^NSEI for India

    try:
        df = yf.download(symbol, period="5y", interval="1d", progress=False)

        if df.empty:
            print("Index load failed")
            return None

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df = df[["Close"]].copy()
        df = df.apply(pd.to_numeric, errors="coerce")
        df.dropna(inplace=True)

        return df

    except Exception as e:
        print("Index error:", e)
        return None


# ================= MAIN LOADER =================
def load_data(DATA_DIR, index_symbol="^GSPC"):

    data = {}

    # 🔥 Load index ONCE
    index_df = load_index_data(index_symbol)

    if index_df is None:
        print("❌ Cannot proceed without index data")
        return {}

    for file in os.listdir(DATA_DIR):

        if not file.endswith(".csv"):
            continue

        path = os.path.join(DATA_DIR, file)

        try:
            # ===== READ RAW =====
            df = pd.read_csv(path)

            # ===== FIX YAHOO MULTI HEADER =====
            if df.iloc[0, 0] == "Ticker":
                df = pd.read_csv(path, skiprows=2)

            # ===== DATE =====
            if "Date" not in df.columns:
                print(f"Skipping {file} → No Date")
                continue

            df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
            df.dropna(subset=["Date"], inplace=True)
            df.set_index("Date", inplace=True)

            # ===== OHLCV =====
            required_cols = ["Open", "High", "Low", "Close", "Volume"]

            if not all(col in df.columns for col in required_cols):
                print(f"Skipping {file} → Missing OHLCV")
                continue

            df = df[required_cols]

            # ===== NUMERIC CLEAN =====
            df = df.apply(pd.to_numeric, errors="coerce")
            df.dropna(inplace=True)

            if len(df) < 300:
                print(f"Skipping {file} → Not enough data")
                continue

            # ===== INDICATORS =====
            df = add_indicators(df)

            if df.empty:
                continue

            # 🔥🔥🔥 ADD RS (MANDATORY FIX)
            df = add_relative_strength(df, index_df)

            # ===== FINAL SAFETY =====
            required_final = ["EMA20", "EMA50", "SMA150", "RS"]

            if not all(col in df.columns for col in required_final):
                print(f"Skipping {file} → Missing final indicators")
                continue

            # Drop rows where indicators not ready
            df.dropna(inplace=True)

            if len(df) < 100:
                continue

            symbol = file.replace(".csv", "")
            data[symbol] = df

        except Exception as e:
            print(f"Skipping {file} → Error: {e}")

    print(f"\n✅ Loaded stocks: {len(data)}")
    return data


# ================= INDICATORS =================
def add_indicators(df):

    try:
        df = df.copy()

        df = df.apply(pd.to_numeric, errors="coerce")
        df.dropna(inplace=True)

        # ===== MOVING AVERAGES =====
        df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()
        df["EMA50"] = df["Close"].ewm(span=50, adjust=False).mean()
        df["EMA220"] = df["Close"].ewm(span=220, adjust=False).mean()
        df["VOL_AVG20"] = df["Volume"].rolling(20).mean()

        df["SMA150"] = df["Close"].rolling(150).mean()

        # ===== 52W HIGH =====
        df["52W_HIGH"] = df["Close"].rolling(252).max()

        # ===== ATR =====
        tr = pd.concat([
            df["High"] - df["Low"],
            (df["High"] - df["Close"].shift()).abs(),
            (df["Low"] - df["Close"].shift()).abs()
        ], axis=1).max(axis=1)

        df["ATR"] = tr.rolling(14).mean()
        df["ATR_PCT"] = df["ATR"] / df["Close"] * 100

        return df

    except Exception as e:
        print("Indicator error:", e)
        return pd.DataFrame()