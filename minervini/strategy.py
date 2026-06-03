# strategy.py
import pandas as pd

def check_entry(df, i, CONFIG, symbol, debug=False):

    if debug: print(f"checking {symbol}")

    cfg = CONFIG.copy()
    if cfg["MARKET"] == "INDIA":
        cfg["BREAKOUT_VOLUME_MULT"] = 1.2
        cfg["BREAKOUT_STRENGTH"] = 0.65
        cfg["MIN_NEAR_HIGH"] = 0.75
        cfg["RS_LOOKBACK"] = 4
        cfg["TOP_N"] = 2
        return check_entry_india(df, i, cfg, debug)

    # if check_200ema_touch_and_near_high(df, i, debug=False):
    #     if debug: print("200 ema")
    #     return ""
    # else:
    #     return "failed 200 EMA"

    if i < max(cfg["MIN_DAYS"], cfg["RS_LOOKBACK"]):
        if debug: print("FAIL RS_LOOKBACK")
        return ("FAIL RS_LOOKBACK")

    row = df.iloc[i]

    required = ["Close", "High", "Low", "Volume",
                "EMA20", "EMA50", "SMA150", "RS"]

    # ===== SAFETY =====
    if not all(col in df.columns for col in required):
        if debug: print("FAIL SAFETY")
        return ("FAIL RS_LOOKBACK")

    if any(pd.isna(row[col]) for col in required):
        return ("FAIL REQUIRED COL")

    # ===== TREND =====
    if not (row["Close"] > row["EMA50"] > row["SMA150"]):
        if debug: print("FAIL TREND")
        return ("FAIL TREND")

    # Avoid overextended stocks
    if row["Close"] > cfg["MAX_EXTENSION"] * row["EMA50"]:
        if debug: print("FAIL EXTENSION")
        return ("FAIL EXTENSION")

    # ===== RELATIVE STRENGTH =====
    rs_now = df["RS"].iloc[i]
    rs_past = df["RS"].iloc[i - cfg["RS_LOOKBACK"]]

    # ===== VOLUME =====
    avg_vol = df["Volume"].rolling(20).mean().iloc[i]

    if rs_now <= rs_past:
        if debug: print("FAIL RS")
        return ("FAIL RS")

    # 3. RS ACCELERATION (STRONG EDGE)
    rs_now = df["RS"].iloc[i]
    rs_past = df["RS"].iloc[i - cfg["RS_LOOKBACK"]]
    rs_mid = df["RS"].iloc[i - int(cfg["RS_LOOKBACK"] / 2)]

    if not (rs_now > rs_mid > rs_past):
        if debug: print("FAIL RS ACCELERATION")
        return ("FAIL RS ACCELERATION")


    # ===== LIQUIDITY =====
    liquidity = row["Close"] * row["Volume"]

    if cfg["MARKET"] == "US" and liquidity < 5e6:
        if debug: print("FAIL LIQUIDITY")
        return ("FAIL LIQUIDITY")

    # ===== BREAKOUT ZONE =====
    prev_high = df["Close"].rolling(252).max().iloc[i - 1]
    if pd.isna(prev_high):
        return ("FAIL NO PREV HIGH")

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
        return ("FAIL FAR FROM HIGH")

    is_breakout = row["Close"] >= prev_high


    if pd.isna(avg_vol) or avg_vol == 0:
        return ("FAIL NO AVG")

    if is_breakout:
        # strict for breakout
        if row["Volume"] < cfg["BREAKOUT_VOLUME_MULT"] * avg_vol:
            if debug: print("FAIL VOL BREAKOUT")
            return ("FAIL VOL BREAKOUT")
    else:
        # mild confirmation for pre-breakout
        if row["Volume"] < 1.05 * avg_vol:
            if debug: print("FAIL VOL PRE")
            return ("FAIL VOL PRE")

    # ===== BREAKOUT STRENGTH =====
    candle_range = row["High"] - row["Low"]

    if candle_range <= 0:
        if debug: print("FAIL BREAKOUT STRENGTH")
        return "FAIL BREAKOUT STRENGT"

    strength = (row["Close"] - row["Low"]) / candle_range

    if strength < cfg["BREAKOUT_STRENGTH"]:
        if debug: print("FAIL STRENGTH")
        return "FAIL STRENGTH"

    # avoid weak closes
    if row["Close"] < 0.4 * (row["High"] - row["Low"]) + row["Low"] and cfg["MARKET"] == "INDIA":
        if debug: print("FAIL WEAK CLOSE")
        return "FAIL WEAK CLOSE"

    return ""

def check_entry_india(df, i, cfg, debug=False):
    fail_reasons = ""
    if i < max(cfg["MIN_DAYS"], cfg["RS_LOOKBACK"]):
        if debug: print("FAIL RS_LOOKBACK")
        return ("FAIL RS_LOOKBACK")

    # change trailinitial and later
    # if detect_vcp_breakout(df, debug= False):
    #     if debug: print("VCP BREAKOUT")
    #     return ""
    # else:
    #     return "FAIL VCP"
    #
    # if check_200ema_touch_and_near_high(df, i, debug=False):
    #     if debug: print("200 ema")
    #     return ""
    # else:
    #     return "failed 200 EMA"

    row = df.iloc[i]

    # TREND
    if not (row["Close"] > row["EMA50"] > row["SMA150"]):
        if debug: print("FAIL trend")
        return "FAIL trend"

    # BREAKOUT
    prev_high = df["Close"].rolling(252).max().iloc[i - 1]
    if pd.isna(prev_high):
        if debug: print("FAIL breakout")
        return "FAIL breakout"

        # 1. MUST BE TRUE BREAKOUT
    if row["Close"] < 1.03 * prev_high:
        if debug: print("FAIL WEAK BREAKOUT")
        return "FAIL WEAK BREAKOUT"

    # avoid chasing
    if row["Close"] > 1.06 * prev_high and not is_bull_snort_breakout(df):
        if debug: print("FAIL avoid chasing 2")
        return "FAIL avoid chasing 2"

    # RS
    rs_now = df["RS"].iloc[i]
    rs_past = df["RS"].iloc[i - cfg["RS_LOOKBACK"]]

    if rs_now <= 1.08 * rs_past:
        if debug: print("FAIL rs_now")
        return "FAIL rs_now"


    # TREND RISING
    if df["EMA50"].iloc[i] <= df["EMA50"].iloc[i - 5]:
        if debug: print("FAIL TREND RISING")
        return "FAIL TREND RISING"

        # ===== LIQUIDITY =====
    liquidity = row["Close"] * row["Volume"]

    if liquidity < 2e7:
        if debug: print("FAIL LIQUIDITY")
        return "FAIL LIQUIDITY"

    # 4. STRONG VOLUME
    avg_vol = df["Volume"].rolling(20).mean().iloc[i]
    if row["Volume"] < 1.2 * avg_vol:
        if debug: print("FAIL VOLUME")
        return "FAIL VOLUME"

    # 5. STRONG FOLLOW-THROUGH
    if row["Close"] < 0.9 * row["High"]:
        if debug: print("FAIL WEAK CLOSE")
        return "FAIL WEAK CLOSE"

    # 6. EMA TREND MUST RISE
    if df["EMA50"].iloc[i] <= df["EMA50"].iloc[i - 5]:
        if debug: print("FAIL EMA50 TREND")
        return "FAIL EMA50 TREND"

        # 3. NO OVERHEAD SUPPLY
    high_20 = df["High"].rolling(20).max().iloc[i - 1]

    if row["Close"] < high_20:
        if debug: print("FAIL OVERHEAD SUPPLY")
        return "FAIL OVERHEAD SUPPLY"

    # expansion candle
    if (row["High"] - row["Low"]) < 1.2 * (df["High"] - df["Low"]).rolling(10).mean().iloc[i]:
        if debug: print("FAIL expansion candle")
        return "FAIL expansion candle"

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

    return fail_reasons

def is_bull_snort_breakout(df,
                          lookback=20,
                          vol_mult=2.5,
                          close_strength=0.7):
    """
    Detects a 'bull snort breakout':
    - Breakout above recent high
    - Volume spike
    - Strong close near high
    """

    if len(df) < lookback + 2:
        return False

    latest = df.iloc[-1]
    prev = df.iloc[-2]

    # --- 1. Breakout above recent high ---
    recent_high = df['High'].iloc[-lookback-1:-1].max()
    breakout = latest['Close'] > recent_high

    # --- 2. Volume spike ---
    avg_vol = df['Volume'].iloc[-lookback-1:-1].mean()
    vol_spike = latest['Volume'] >= vol_mult * avg_vol

    # --- 3. Strong close (close near high of candle) ---
    candle_range = latest['High'] - latest['Low']
    if candle_range == 0:
        return False

    close_position = (latest['Close'] - latest['Low']) / candle_range
    strong_close = close_position >= close_strength

    # --- Final condition ---
    return breakout and vol_spike and strong_close


def detect_vcp_breakout(dataF, debug=False):
    """
    df must have columns: ['Open', 'High', 'Low', 'Close', 'Volume']
    timeframe: ~1 year daily data
    """
    df = dataF.copy()

    # --- 1. Moving averages for trend ---
    df.loc[:, "ema20"] = df["Close"].ewm(span=20).mean()
    df.loc[:, "ema50"] = df["Close"].ewm(span=50).mean()

    # Uptrend condition
    if not (df["Close"].iloc[-1] > df["ema20"].iloc[-1] > df["ema50"].iloc[-1]):
        if debug: print("FAIL: No uptrend")
        return False

    # --- 2. Identify swing highs/lows ---
    window = 5
    # Initialize columns with NaN
    df.loc[:, "swing_high"] = float('nan')
    df.loc[:, "swing_low"] = float('nan')

    # Identify peaks and valleys using rolling logic
    high_mask = (df["High"].rolling(window, center=True).max() == df["High"])
    low_mask = (df["Low"].rolling(window, center=True).min() == df["Low"])

    # Use .loc for safe assignment
    df.loc[high_mask, "swing_high"] = df["High"]
    df.loc[low_mask, "swing_low"] = df["Low"]

    swing_highs = df["swing_high"].dropna()
    swing_lows = df["swing_low"].dropna()

    if len(swing_highs) < 3 or len(swing_lows) < 3:
        if debug: print("FAIL: Not enough swings")
        return False

    # --- 3. Contraction check (ranges getting tighter) ---
    ranges = []
    # Use latest 3-4 swings
    for i in range(1, min(5, len(swing_highs))):
        high = swing_highs.iloc[-i]
        # Match with the corresponding low (this logic assumes 1:1 high-low pairs)
        low = swing_lows.iloc[-i]
        ranges.append((high - low) / low)

    # Check for decreasing volatility (contraction)
    # Reversing because we appended the most recent first
    if not all(x < y for x, y in zip(ranges, ranges[1:])):
        if debug: print(f"FAIL: No contraction. Ranges: {[f'{r:.2%}' for r in ranges]}")
        return False

    # --- 4. Volume contraction ---
    recent_vol = df["Volume"].iloc[-20:].mean()
    # Past volume (rows -60 to -20)
    past_vol = df["Volume"].iloc[-60:-20].mean()

    if not (recent_vol < past_vol):
        if debug: print(f"FAIL: Volume not drying. Recent: {recent_vol:.0f}, Past: {past_vol:.0f}")
        return False

    # --- 5. Breakout ---
    resistance = swing_highs.iloc[-3:].max()
    latest_close = df["Close"].iloc[-1]
    breakout_volume = df["Volume"].iloc[-1]
    avg_volume = df["Volume"].iloc[-20:].mean()

    if latest_close > resistance and breakout_volume > 1.5 * avg_volume:
        print(f"PASS: VCP Breakout detected!")
        print(f"Close: {latest_close} > Res: {resistance}")
        return True

    if debug: print("FAIL: No breakout")
    # results with below custom config
    # "TRAIL_INITIAL": 0.90,
    # "TRAIL_AFTER_PARTIAL": 0.90,
    return False


def check_200ema_touch_and_near_high(dataF, i, debug=False):
    """
    df must have: ['Open', 'High', 'Low', 'Close']
    timeframe: at least 1 year daily data
    """
    # Create a full copy to avoid modifying the original dataF
    df = dataF.copy()

    # --- 1. Calculate 200 EMA ---
    df["ema200"] = df["Close"].ewm(span=200, adjust=False).mean()

    # --- 2. Check touch in last 100 days relative to index i ---
    # We take the 100 rows leading up to i
    start_idx = max(0, i - 99)
    recent = df.iloc[start_idx: i + 1].copy()  # .copy() fixes the SettingWithCopyWarning

    # Define "touch" as within 2% of EMA
    recent.loc[:, "ema_diff_pct"] = abs(recent["Close"] - recent["ema200"]) / recent["ema200"]
    touched_ema = (recent["ema_diff_pct"] < 0.02).any()

    if not touched_ema:
        if debug: print(f"FAIL: No EMA200 touch in last 100 days at index {i}")
        return False

    # --- 3. 80 days high -> 16-week high (relative to index i) ---
    high_start = max(0, i - 80)
    high_52w = df["High"].iloc[high_start: i + 1].max()
    current_price = df["Close"].iloc[i]

    # Within 3% of high (based on your 0.97 multiplier)
    near_high = current_price >= 0.97 * high_52w

    if not near_high:
        if debug: print(f"FAIL: Not near 52-week high (Price: {current_price}, High: {high_52w})")
        return False

    # --- 4. STRONG VOLUME ---
    # Rolling mean needs enough data before index i
    avg_vol_series = df["Volume"].rolling(20).mean()
    avg_vol = avg_vol_series.iloc[i]

    current_vol = df["Volume"].iloc[i]
    if current_vol < 1.5 * avg_vol:
        if debug: print(f"FAIL VOLUME: {current_vol} < {1.3 * avg_vol:.0f}")
        return False

    if debug:
        print(f"PASS at index {i}:")
        print(f"Current Price: {current_price}")
        print(f"52W High: {high_52w}")
        print(f"Distance from High: {(high_52w - current_price) / high_52w:.2%}")
    # 125 days - 2.0 0.75 {'Return %': 30, 'Win Rate': 62, 'Expectancy': 6, 'avg win': 14, 'avg loss': -9, 'Max DD': -6, 'Trades': 87}
    # 80 days high - {'Return %': 37, 'Win Rate': 63, 'Expectancy': 5, 'avg win': 13, 'avg loss': -9, 'Max DD': -6, 'Trades': 100}
    # 251 days {'Return %': 25, 'Win Rate': 57, 'Expectancy': 5, 'avg win': 16, 'avg loss': -9, 'Max DD': -7, 'Trades': 81}
    return True