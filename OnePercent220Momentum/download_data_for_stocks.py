import os
import pandas as pd
import yfinance as yf
from tqdm import tqdm

# === CONFIG ===
CSV_FILE = "nasdaq.csv"  # change to your actual file name
OUTPUT_DIR = "data"
START_DATE = "2024-01-01"
END_DATE = None  # None = till today

# === CREATE DATA FOLDER ===
os.makedirs(OUTPUT_DIR, exist_ok=True)

# === LOAD SYMBOLS ===
df = pd.read_csv(CSV_FILE)

if "Symbol" not in df.columns:
    raise ValueError("CSV must contain a 'Symbol' column")

symbols = df["Symbol"].dropna().unique().tolist()

print(f"Total symbols: {len(symbols)}")

# === DOWNLOAD LOOP ===
for symbol in tqdm(symbols, desc="Downloading data"):
    try:
        data = yf.download(
            symbol,
            start=START_DATE,
            end=END_DATE,
            interval="1d",
            auto_adjust=False,
            progress=False
        )

        if data.empty:
            print(f"No data for {symbol}")
            continue

        # Reset index to have Date column
        data.reset_index(inplace=True)

        # Save file
        file_path = os.path.join(OUTPUT_DIR, f"{symbol}.csv")
        data.to_csv(file_path, index=False)

    except Exception as e:
        print(f"Error downloading {symbol}: {e}")

print("✅ Data download complete.")