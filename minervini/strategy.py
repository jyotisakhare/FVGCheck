# strategy.py
import pandas as pd
import numpy as np


def check_entry(df, i, CONFIG, debug=False):
    cfg = CONFIG.copy()
    if cfg["MARKET"] == "INDIA":
        cfg["BREAKOUT_VOLUME_MULT"] = 1.2
        cfg["BREAKOUT_STRENGTH"] = 0.65
        cfg["MIN_NEAR_HIGH"] = 0.75
        cfg["RS_LOOKBACK"] = 4
        cfg["TOP_N"] = 1
        return check_entry_india(df, i, cfg, debug)


    if i < max(cfg["MIN_DAYS"], cfg["RS_LOOKBACK"]):
        if debug: print("FAIL RS_LOOKBACK")
        return False

    row = df.iloc[i]

    required = ["Close", "High", "Low", "Volume",
                "EMA20", "EMA50", "SMA150", "RS"]

    # ===== SAFETY =====
    if not all(col in df.columns for col in required):
        if debug: print("FAIL SAFETY")
        return False

    if any(pd.isna(row[col]) for col in required):
        return False

    # ===== TREND =====
    if not (row["Close"] > row["EMA50"] > row["SMA150"]):
        if debug: print("FAIL TREND")
        return False

    # Avoid overextended stocks
    if row["Close"] > cfg["MAX_EXTENSION"] * row["EMA50"]:
        if debug: print("FAIL EXTENSION")
        return False

    # ===== RELATIVE STRENGTH =====
    rs_now = df["RS"].iloc[i]
    rs_past = df["RS"].iloc[i - cfg["RS_LOOKBACK"]]

    # ===== BREAKOUT ZONE =====
    prev_high = df["Close"].rolling(252).max().iloc[i - 1]

    # ===== VOLUME =====
    avg_vol = df["Volume"].rolling(20).mean().iloc[i]


    # STRICT INDIA VERSION

    if cfg["MARKET"] == "INDIA":
        distance = row["Close"] / prev_high
        # near highs
        if distance < 0.90:
            return False

        # only breakout trades
        if row["Close"] < prev_high:
            return False

        # avoid late entries near exhaustion
        if row["Close"] > 1.05 * prev_high:
            return False

        # strong RS
        if rs_now <= 1.05 * rs_past:
            return False

        # stronger volume
        if row["Volume"] < 1.2 * avg_vol:
            return False

        # trend must be rising
        if df["EMA50"].iloc[i] <= df["EMA50"].iloc[i - 5]:
            return False

        # volatility contraction before breakout
        range_mean = (df["High"] - df["Low"]).rolling(10).mean().iloc[i]
        range_past = (df["High"] - df["Low"]).rolling(30).mean().iloc[i]

        if range_mean > range_past:
            return False


    if rs_now <= rs_past:
        if debug: print("FAIL RS")
        return False

    # ===== LIQUIDITY =====
    liquidity = row["Close"] * row["Volume"]

    if cfg["MARKET"] == "US" and liquidity < 5e6:
        if debug: print("FAIL LIQUIDITY")
        return False

    if cfg["MARKET"] == "INDIA" and liquidity < 2e7:
        if debug: print("FAIL LIQUIDITY")
        return False

    if pd.isna(prev_high):
        return False

    distance = row["Close"] / prev_high

    # Must be near highs
    if distance < cfg["MIN_NEAR_HIGH"]:
        if debug: print("FAIL FAR FROM HIGH")
        return False

    is_breakout = row["Close"] >= prev_high


    if pd.isna(avg_vol) or avg_vol == 0:
        return False

    if is_breakout:
        # strict for breakout
        if row["Volume"] < cfg["BREAKOUT_VOLUME_MULT"] * avg_vol:
            if debug: print("FAIL VOL BREAKOUT")
            return False
    else:
        # mild confirmation for pre-breakout
        if row["Volume"] < 1.05 * avg_vol:
            if debug: print("FAIL VOL PRE")
            return False

    # ===== BREAKOUT STRENGTH =====
    candle_range = row["High"] - row["Low"]

    if candle_range <= 0:
        return False

    strength = (row["Close"] - row["Low"]) / candle_range

    if strength < cfg["BREAKOUT_STRENGTH"]:
        if debug: print("FAIL STRENGTH")
        return False

    # avoid weak closes
    if row["Close"] < 0.4 * (row["High"] - row["Low"]) + row["Low"] and cfg["MARKET"] == "INDIA":
        if debug: print("FAIL WEAK CLOSE")
        return False

    return True

def check_entry_india(df, i, cfg, debug=False):

    if i < max(cfg["MIN_DAYS"], cfg["RS_LOOKBACK"]):
        if debug: print("FAIL RS_LOOKBACK")
        return False

    row = df.iloc[i]

    # TREND
    if not (row["Close"] > row["EMA50"] > row["SMA150"]):
        if debug: print("FAIL trend")
        return False

    # BREAKOUT
    prev_high = df["Close"].rolling(252).max().iloc[i - 1]
    if pd.isna(prev_high):
        if debug: print("FAIL breakout")
        return False

    if row["Close"] < prev_high:
        if debug: print("FAIL breakout 2")
        return False

    # avoid chasing
    if row["Close"] > 1.08 * prev_high:
        if debug: print("FAIL avoid chasing 2")
        return False

    # RS
    rs_now = df["RS"].iloc[i]
    rs_past = df["RS"].iloc[i - cfg["RS_LOOKBACK"]]

    if rs_now <= 1.05 * rs_past:
        if debug: print("FAIL rs_now")
        return False

    # VOLUME
    avg_vol = df["Volume"].rolling(20).mean().iloc[i]
    if row["Volume"] < 1.2 * avg_vol:
        if debug: print("FAIL Volume")
        return False

    # FOLLOW THROUGH (NEW EDGE)
    if row["Close"] <= df["High"].iloc[i - 1]:
        if debug: print("FAIL NEW EDGE")
        return False

    # TREND RISING
    if df["EMA50"].iloc[i] <= df["EMA50"].iloc[i - 5]:
        if debug: print("FAIL TREND RISING")
        return False

    return True