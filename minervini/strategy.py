# strategy.py
import pandas as pd
import numpy as np

def check_entry(df, i, cfg, debug = False):
    # TEMP DEBUG
    # print("Checking:", df.index[i])

    if i < max(cfg["MIN_DAYS"], cfg["RS_LOOKBACK"]):
        return False

    row = df.iloc[i]

    required = ["Close", "High", "Low", "Volume",
                "EMA20", "EMA50", "SMA150", "RS"]

    if not all(col in df.columns for col in required):
        return False

    if any(pd.isna(row[col]) for col in required):
        return False

    # ===== TREND =====
    if not (row["Close"] > row["EMA20"] > row["EMA50"] > row["SMA150"]):
        return False

    # ===== BREAKOUT (relaxed) =====
    prev_high = df["Close"].rolling(252).max().iloc[i - 1]

    if pd.isna(prev_high) or row["Close"] < 0.98 * prev_high:
        return False

    # ===== STRENGTH =====
    candle_range = row["High"] - row["Low"]
    if candle_range <= 0:
        return False

    strength = (row["Close"] - row["Low"]) / candle_range
    if strength < cfg["BREAKOUT_STRENGTH"]:
        return False

    # ===== VOLUME =====
    avg_vol = df["Volume"].rolling(20).mean().iloc[i]
    if pd.isna(avg_vol) or avg_vol == 0:
        return False

    if row["Volume"] < 1.2 * avg_vol:
        return False

    # ===== RS MOMENTUM =====
    if df["RS"].iloc[i] <= df["RS"].iloc[i - cfg["RS_LOOKBACK"]]:
        return False

    # ===== LIQUIDITY =====
    liquidity = row["Close"] * row["Volume"]

    if cfg["MARKET"] == "US" and liquidity < 5e6:
        return False

    if cfg["MARKET"] == "INDIA" and liquidity < 2e7:
        return False

    return True