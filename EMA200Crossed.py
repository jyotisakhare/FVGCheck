import yfinance as yf
import pandas as pd
import numpy as np

# -----------------------------
# Indicator Functions
# -----------------------------

def add_indicators(df):
    # EMA
    df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
    df['EMA50'] = df['Close'].ewm(span=50, adjust=False).mean()

    # ATR (14)
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift(1))
    low_close = np.abs(df['Low'] - df['Close'].shift(1))

    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df['ATR'] = tr.rolling(14).mean()

    # CCI (20)
    tp = (df['High'] + df['Low'] + df['Close']) / 3
    sma = tp.rolling(20).mean()
    mad = tp.rolling(20).apply(lambda x: np.mean(np.abs(x - np.mean(x))), raw=True)
    df['CCI'] = (tp - sma) / (0.015 * mad)

    return df


# -----------------------------
# Scoring Function
# -----------------------------

def calculate_score(df):
    score = 0

    # Always use iloc → guarantees scalar
    close = df['Close'].iloc[-1]
    ema20 = df['EMA20'].iloc[-1]
    ema50 = df['EMA50'].iloc[-1]
    atr = df['ATR'].iloc[-1]
    volume = df['Volume'].iloc[-1]

    # 1. Close > EMA50 (10%)
    if close > ema50:
        score += 10

    # 2. Close > EMA20 (10%)
    if close > ema20:
        score += 10

    # 3. EMA20 > EMA50 (20%)
    if ema20 > ema50:
        score += 20

    # 4. Within 20% of 52-week high (30%)
    high_52w = df['Close'].rolling(252).max().iloc[-1]
    if close >= 0.8 * high_52w:
        score += 30

    # 5. ATR % < 3% (10%)
    if pd.notna(atr) and close != 0:
        atr_pct = (atr / close) * 100
        if atr_pct < 3:
            score += 10

    # 6. CCI rising (slope method) (10%)
    cci_last20 = df['CCI'].iloc[-20:].dropna()
    if len(cci_last20) == 20:
        x = np.arange(20)
        slope = np.polyfit(x, cci_last20.values, 1)[0]
        if slope > 0:
            score += 10

    # 7. Volume > 20-day avg (5%)
    vol_avg_20 = df['Volume'].rolling(20).mean().iloc[-1]
    if volume > vol_avg_20:
        score += 5

    # 8. Last 2 days > last 5 days volume (5%)
    avg_2 = df['Volume'].iloc[-2:].mean()
    avg_5 = df['Volume'].iloc[-5:].mean()
    if avg_2 > avg_5:
        score += 5

    return score


# -----------------------------
# Main Analysis Function
# -----------------------------

def analyze_stocks(symbols):
    results = []

    for symbol in symbols:
        try:
            df = yf.download(symbol+".NS", period="1y", interval="1d", progress=False)

            if df.empty or len(df) < 100:
                continue

            # 🔥 Fix multi-index issue (CRITICAL)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            # Keep only required columns
            df = df[['Open', 'High', 'Low', 'Close', 'Volume']].copy()

            # Clean data
            df.dropna(inplace=True)

            # Ensure numeric
            df = df.astype(float)

            # Add indicators
            df = add_indicators(df)

            # Calculate score
            score = calculate_score(df)

            if score > 65:
                results.append({
                    "Symbol": symbol,
                    "Score": score
                })

        except Exception as e:
            print(f"Error with {symbol}: {e}")

    result_df = pd.DataFrame(results)

    if not result_df.empty:
        result_df = result_df.sort_values(by="Score", ascending=False)

    return result_df




# -----------------------------
# Example Usage
# -----------------------------


# === CONFIG ===
CSV_FILE = "nifty500.csv"  # change to your actual file name
OUTPUT_DIR = "data"
START_DATE = "2025-01-01"
END_DATE = None  # None = till today

# === CREATE DATA FOLDER ===
# os.makedirs(OUTPUT_DIR, exist_ok=True)

# === LOAD SYMBOLS ===
df = pd.read_csv(CSV_FILE)

if "Symbol" not in df.columns:
    raise ValueError("CSV must contain a 'Symbol' column")

symbols = df["Symbol"].dropna().unique().tolist()

result = analyze_stocks(symbols)
print(result)