import pandas as pd
import os

def load_market_symbols(base_path=""):
    market_files = {
        "US": "nasdaq.csv",
        "INDIA": "nifty500.csv",
    }

    markets = {}

    for market, file in market_files.items():
        path = os.path.join(base_path, file)

        if not os.path.exists(path):
            print(f"⚠️ Missing file: {file}")
            markets[market] = []
            continue

        try:
            df = pd.read_csv(path)

            df.columns = [c.strip().lower() for c in df.columns]

            if "symbol" not in df.columns:
                raise ValueError(f"{file} must contain 'Symbol' column")

            symbols = (
                df["symbol"]
                .dropna()
                .astype(str)
                .str.strip()
                .unique()
                .tolist()
            )

            markets[market] = symbols

        except Exception as e:
            print(f"❌ Error loading {file}: {e}")
            markets[market] = []

    return markets