import pandas as pd
import yfinance as yf
# nifty500.csv
# nasdaq.csv
def load_symbols(filename = "nifty500.csv"):
    df = pd.read_csv(filename)
    return df["Symbol"].dropna().unique().tolist()

def scan_weekly_momentum(symbol):
    print(f"Scanning US Momentum {symbol}".format(symbol=symbol))
    try:
        # Fetch daily data and resample to weekly (W-FRI) to replicate weekly chart scans
        df_daily = yf.download(symbol, period="2y", interval="1d", progress=False)
        if df_daily.empty or len(df_daily) < 300:
            return None

        # Clean multi-index columns if present
        if isinstance(df_daily.columns, pd.MultiIndex):
            df_daily.columns = df_daily.columns.get_level_values(0)

        # Resample to weekly close and volume
        df_weekly = df_daily.resample("W-FRI").agg({
            "Close": "last",
            "High": "max",
            "Low": "min",
            "Volume": "sum"
        }).dropna()

        if len(df_weekly) < 60:
            return None

        # Calculate 52-week high on weekly bars (~52 weeks)
        df_weekly["52W_High"] = df_weekly["High"].rolling(window=52).max()

        # Momentum checks (similar to weekly high criteria)
        current_close = df_weekly["Close"].iloc[-1]
        prev_close_1 = df_weekly["Close"].iloc[-2]
        prev_close_2 = df_weekly["Close"].iloc[-3]

        # Weekly price change versus the previous weekly close
        weekly_change_pct = ((current_close / prev_close_1) - 1) * 100

        high_52w = df_weekly["52W_High"].iloc[-1]
        avg_vol = df_weekly["Volume"].rolling(20).mean().iloc[-1]

        # Criteria: Close is near or breaking 52-week high and average weekly volume is solid
        near_high = current_close >= (0.90 * high_52w)
        is_liquid = avg_vol > 500000

        if near_high and is_liquid:
            return {
                "Symbol": symbol,
                "Close": round(current_close, 2),
                "Weekly Change_%": round(weekly_change_pct, 2),
                "52W High": round(high_52w, 2),
                "DistanceFromHigh_%": round(((current_close - high_52w) / high_52w) * 100, 2),
                "Avg Weekly Vol": int(avg_vol)
            }
    except Exception as e:
        print(e)
        pass
    return None

# Run scanner across universe
print("Running US Weekly Momentum Scan...")
results = [scan_weekly_momentum(t) for t in load_symbols()]
scanned_df = pd.DataFrame([r for r in results if r is not None])

if not scanned_df.empty:
    print(scanned_df.sort_values(by="DistanceFromHigh_%", ascending=False).to_string(index=False))
else:
    print("No stocks matched the criteria in the current universe scan.")