import datetime

import pandas as pd
import yfinance as yf
from pathlib import Path

# nifty500.csv
# nasdaq.csv
def load_symbols(filename = "nasdaq.csv"):
    df = pd.read_csv(filename)
    return df["Symbol"].dropna().unique().tolist()

def scan_weekly_momentum(symbol):
    print(f"Scanning Weekly Momentum {symbol}")

    try:
        # Explicit adjustment setting for consistent results.
        df_daily = yf.download(
            symbol,
            period="2y",
            interval="1d",
            auto_adjust=False,
            progress=False,
        )

        if df_daily.empty or len(df_daily) < 300:
            return None

        # Clean multi-index columns for a single-symbol download.
        if isinstance(df_daily.columns, pd.MultiIndex):
            df_daily.columns = df_daily.columns.get_level_values(0)

        df_daily = df_daily.sort_index()

        # Resample to weekly close, high, low and total volume.
        df_weekly = df_daily.resample("W-FRI").agg({
            "Close": "last",
            "High": "max",
            "Low": "min",
            "Volume": "sum",
        }).dropna()

        if len(df_weekly) < 60:
            return None

        # Conventional 52-week intraday high: retained for your output.
        df_weekly["52W_High"] = (
            df_weekly["High"].rolling(window=52).max()
        )

        # Screenshot uses WEEKLY CLOSE, not weekly High.
        # Shift by one to exclude the week being tested.
        df_weekly["Prior_52W_Closing_High"] = (
            df_weekly["Close"]
            .rolling(window=52)
            .max()
            .shift(1)
        )

        current_close = float(df_weekly["Close"].iloc[-1])
        prev_close_1 = float(df_weekly["Close"].iloc[-2])

        if prev_close_1 <= 0:
            return None

        weekly_change_pct = (
            (current_close / prev_close_1) - 1
        ) * 100

        high_52w = float(df_weekly["52W_High"].iloc[-1])
        prior_closing_high = float(
            df_weekly["Prior_52W_Closing_High"].iloc[-1]
        )

        avg_vol = float(
            df_weekly["Volume"].rolling(20).mean().iloc[-1]
        )

        # Existing conditions.
        near_high = current_close >= (0.90 * high_52w)
        is_liquid = avg_vol > 500000

        # NEW: Current close > prior 52-week maximum weekly close.
        fresh_breakout = current_close > prior_closing_high

        # NEW: Each previous five weeks closed below its own
        # preceding 52-week maximum weekly close.
        previous_five_below = all(
            df_weekly["Close"].iloc[-1 - weeks_ago]
            < df_weekly["Prior_52W_Closing_High"].iloc[
                -1 - weeks_ago
            ]
            for weeks_ago in range(1, 6)
        )
        # print(f"{near_high} {is_liquid} {fresh_breakout} {previous_five_below}")
        # Check price/volume filters before requesting metadata.
        if not (
            near_high
            and is_liquid
            and fresh_breakout
            and previous_five_below
        ):
            return None

        # # NEW: Market cap between INR 2,000 and 50,000 crore.
        info = yf.Ticker(symbol).get_info()
        market_cap = info.get("marketCap")
        market_cap_cr = float(market_cap) / 10_000_000
        # currency = info.get("currency")
        #
        # # Prevent applying INR thresholds to USD or other currencies.
        # if currency != "INR":
        #     print(
        #         f"Skipping {symbol}: INR market-cap limits require "
        #         f"INR data; received {currency!r}."
        #     )
        #     return None
        #
        # if market_cap is None or pd.isna(market_cap):
        #     print(f"Skipping {symbol}: market cap unavailable.")
        #     return None
        #
        #
        # market_cap_ok = 2000 <= market_cap_cr <= 50000
        #
        # if not market_cap_ok:
        #     return None

        return {
            "Symbol": symbol,
            "Close": round(current_close, 2),
            "Weekly Change_%": round(weekly_change_pct, 2),
            "52W High": round(high_52w, 2),
            "DistanceFromHigh_%": round(
                ((current_close - high_52w) / high_52w) * 100,
                2,
            ),
            "Avg Weekly Vol": int(avg_vol),
            "Prior 52W Closing High": round(prior_closing_high, 2),
            "Market Cap (INR Cr)": round(market_cap_cr, 2),
        }

    except Exception as e:
        print(f"Error scanning {symbol}: {e}")

    return None
# Run scanner across universe
print("Running Weekly Momentum Scan...")

symbols = load_symbols()
results = []

for symbol in symbols:
    result = scan_weekly_momentum(symbol)

    # Only collect valid dictionaries.
    if isinstance(result, dict) and result:
        results.append(result)

print(f"\nTotal symbols scanned: {len(symbols)}")
print(f"Stocks matching filters: {len(results)}")

if results:
    df_results = pd.DataFrame(results)

    # Sort strongest weekly gain first.
    df_results = df_results.sort_values(
        by="Weekly Change_%",
        ascending=False,
    ).reset_index(drop=True)

    # Keep your existing `import datetime`.
    filename = (
        f"weekly_momentum_results_"
        f"{datetime.datetime.now():%Y%m%d_%H%M%S}.csv"
    )

    output_path = Path.cwd() / filename

    df_results.to_csv(
        output_path,
        index=False,
        encoding="utf-8-sig",
    )

    print(df_results.to_string(index=False))
    print(f"\nCSV saved to: {output_path}")

else:
    print("No stocks matched the criteria. No CSV file created.")