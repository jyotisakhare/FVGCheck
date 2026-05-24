import yfinance as yf
import pandas as pd
import os

SAVE_DIR = "../data_us"
SYMBOL_FILE = "nasdaq.csv"   # one column: Symbol

os.makedirs(SAVE_DIR, exist_ok=True)


def clean_yahoo_df(df):
    try:
        # ===== HANDLE MULTI-INDEX =====
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # ===== STANDARDIZE COLUMN NAMES =====
        df.columns = [col.strip().title() for col in df.columns]

        # Fix Adj Close → Close
        if "Adj Close" in df.columns:
            df["Close"] = df["Adj Close"]

        # Keep only required
        required = ["Open", "High", "Low", "Close", "Volume"]
        df = df[[col for col in required if col in df.columns]]

        # Ensure all required exist
        if len(df.columns) < 5:
            return None

        # ===== FORCE NUMERIC =====
        df = df.apply(pd.to_numeric, errors="coerce")

        # Drop bad rows
        df.dropna(inplace=True)

        return df

    except Exception as e:
        print("Cleaning error:", e)
        return None


def download_symbol(symbol):
    try:
        print(f"Downloading {symbol}...")

        df = yf.download(
            symbol,
            period="5y",
            interval="1d",
            auto_adjust=False,
            progress=False
        )

        if df.empty:
            print(f"❌ No data: {symbol}")
            return

        df = clean_yahoo_df(df)

        if df is None or len(df) < 300:
            print(f"❌ Skipped (bad data): {symbol}")
            return

        # ===== SAVE CLEAN CSV =====
        df.reset_index(inplace=True)
        df.rename(columns={"Date": "Date"}, inplace=True)

        save_path = os.path.join(SAVE_DIR, f"{symbol}.csv")
        df.to_csv(save_path, index=False)

        print(f"✅ Saved: {symbol}")

    except Exception as e:
        print(f"❌ Error {symbol}: {e}")


def run_download():
    symbols = pd.read_csv(SYMBOL_FILE)

    if "Symbol" not in symbols.columns:
        raise ValueError("symbols.csv must have 'Symbol' column")

    for symbol in symbols["Symbol"].dropna().unique():
        download_symbol(symbol)


if __name__ == "__main__":
    run_download()