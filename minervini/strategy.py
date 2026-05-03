# strategy.py
import pandas as pd
import numpy as np


def check_entry(df, i, CONFIG, symbol, debug=False):

    if debug: print(f"checking {symbol}")

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

    # ===== VOLUME =====
    avg_vol = df["Volume"].rolling(20).mean().iloc[i]

    if rs_now <= rs_past:
        if debug: print("FAIL RS")
        return False

    # 3. RS ACCELERATION (STRONG EDGE)
    rs_now = df["RS"].iloc[i]
    rs_past = df["RS"].iloc[i - cfg["RS_LOOKBACK"]]
    rs_mid = df["RS"].iloc[i - int(cfg["RS_LOOKBACK"] / 2)]

    if not (rs_now > rs_mid > rs_past):
        if debug: print("FAIL RS ACCELERATION")
        return False


    # ===== LIQUIDITY =====
    liquidity = row["Close"] * row["Volume"]

    if cfg["MARKET"] == "US" and liquidity < 5e6:
        if debug: print("FAIL LIQUIDITY")
        return False

    # ===== BREAKOUT ZONE =====
    prev_high = df["Close"].rolling(252).max().iloc[i - 1]
    if pd.isna(prev_high):
        return False

    #     # 6. BASE TIGHTNESS (VERY IMPORTANT)
    # range_10 = (df["High"] - df["Low"]).rolling(10).mean().iloc[i]
    # range_30 = (df["High"] - df["Low"]).rolling(30).mean().iloc[i]
    #
    # # stricter for india
    # base_threshold = 0.7 if cfg["MARKET"] == "INDIA" else 0.8
    #
    # if range_10 > base_threshold * range_30:
    #     if debug: print("FAIL LOOSE BASE")
    #     return False

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

        # 1. MUST BE TRUE BREAKOUT
    if row["Close"] < 1.03 * prev_high:
        if debug: print("FAIL WEAK BREAKOUT")
        return False

    # avoid chasing
    if row["Close"] > 1.06 * prev_high:
        if debug: print("FAIL avoid chasing 2")
        return False

    # RS
    rs_now = df["RS"].iloc[i]
    rs_past = df["RS"].iloc[i - cfg["RS_LOOKBACK"]]

    if rs_now <= 1.08 * rs_past:
        if debug: print("FAIL rs_now")
        return False


    # TREND RISING
    if df["EMA50"].iloc[i] <= df["EMA50"].iloc[i - 5]:
        if debug: print("FAIL TREND RISING")
        return False

        # ===== LIQUIDITY =====
    liquidity = row["Close"] * row["Volume"]

    if liquidity < 2e7:
        if debug: print("FAIL LIQUIDITY")
        return False

    # 4. STRONG VOLUME
    avg_vol = df["Volume"].rolling(20).mean().iloc[i]
    if row["Volume"] < 1.2 * avg_vol:
        if debug: print("FAIL VOLUME")
        return False

    # 5. STRONG FOLLOW-THROUGH
    if row["Close"] < 0.9 * row["High"]:
        if debug: print("FAIL WEAK CLOSE")
        return False

    # 6. EMA TREND MUST RISE
    if df["EMA50"].iloc[i] <= df["EMA50"].iloc[i - 5]:
        if debug: print("FAIL EMA50 TREND")
        return False

        # 3. NO OVERHEAD SUPPLY
    high_20 = df["High"].rolling(20).max().iloc[i - 1]

    if row["Close"] < high_20:
        if debug: print("FAIL OVERHEAD SUPPLY")
        return False

    # expansion candle
    if (row["High"] - row["Low"]) < 1.2 * (df["High"] - df["Low"]).rolling(10).mean().iloc[i]:
        return False

    # tight base BEFORE breakout
    # base_range = (df["High"] - df["Low"]).rolling(15).mean().iloc[i]
    # base_range_long = (df["High"] - df["Low"]).rolling(40).mean().iloc[i]
    #
    # if base_range > 0.65 * base_range_long:
    #     return False

    # # breakout must be fresh (not 2nd/3rd day move)
    # if df["Close"].iloc[i - 1] > prev_high:
    #     return False

    # if row["Open"] < prev_high:
    #     return False

    return True