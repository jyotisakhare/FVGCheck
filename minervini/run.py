# run.py
import pandas as pd

from config import CONFIG
from data import load_data
from engine import run_backtest
from metrics import compute_metrics

data = load_data()

best = None

for vol in [2.0]: #[1.3, 1.5, 2.0]
    for strength in [0.75]: #[0.6, 0.7, 0.75]

        cfg = CONFIG.copy()
        cfg["BREAKOUT_VOLUME_MULT"] = vol
        cfg["BREAKOUT_STRENGTH"] = strength
        if cfg["MARKET"] == "INDIA":
            cfg["TOP_N"] = 3

        trades, equity = run_backtest(data, cfg)

        equity_df = pd.DataFrame(equity)

        equity_df["Peak"] = equity_df["Equity"].cummax()
        equity_df["DD"] = (equity_df["Equity"] - equity_df["Peak"]) / equity_df["Peak"]

        max_dd = equity_df["DD"].min() * 100

        print(f"Max Drawdown: {max_dd:.2f}%")

        stats = compute_metrics(trades, equity, cfg["INITIAL_CAPITAL"])

        print(vol, strength, stats)

if best is None or stats["Return %"] > best[0]:
    best = (stats["Return %"], vol, strength)

print("\nBEST:", best)
# India results till 30th APR
# {'Return %': 30, 'Win Rate': 42, 'Expectancy': 3, 'avg win': 17, 'avg loss': -7, 'Max DD': -8, 'Trades': 146}
# US results till 20th APR
# {'Return %': 30, 'Win Rate': 49, 'Expectancy': 4, 'avg win': 19, 'avg loss': -11, 'Max DD': -12, 'Trades': 136}