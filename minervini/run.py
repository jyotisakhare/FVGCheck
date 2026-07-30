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
            cfg["TOP_N"] = 2

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
# India results
# minervini
# 24 jun {'Return %': 43, 'Win Rate': 46, 'Expectancy': 4, 'avg win': 19, 'avg loss': -10, 'Max DD': -12, 'Trades': 317}
# 200 ema
# top 1{'Return %': 114, 'Win Rate': 54, 'Expectancy': 5, 'avg win': 18, 'avg loss': -10, 'Max DD': -15, 'Trades': 525}
# top 2 {'Return %': 86, 'Win Rate': 48, 'Expectancy': 4, 'avg win': 18, 'avg loss': -10, 'Max DD': -13, 'Trades': 580}
# top 2 {'Return %': 105, 'Win Rate': 50, 'Expectancy': 4, 'avg win': 18, 'avg loss': -10, 'Max DD': -12, 'Trades': 611}

# US results till 20th APR
# {'Return %': 35, 'Win Rate': 48, 'Expectancy': 5, 'avg win': 22, 'avg loss': -11, 'Max DD': -14, 'Trades': 122}
# TOP 2 27 may
# {'Return %': 33, 'Win Rate': 48, 'Expectancy': 5, 'avg win': 22, 'avg loss': -11, 'Max DD': -13, 'Trades': 126}
# 200 EMA top 2 with max 20 trades
#  {'Return %': 49, 'Win Rate': 57, 'Expectancy': 6, 'avg win': 19, 'avg loss': -10, 'Max DD': -11, 'Trades': 165}

# minervini
# {'Return %': 38, 'Win Rate': 51, 'Expectancy': 5, 'avg win': 20, 'avg loss': -11, 'Max DD': -13, 'Trades': 229}
# 200 Ema
# top 2 nasdaq {'Return %': 75, 'Win Rate': 58, 'Expectancy': 6, 'avg win': 18, 'avg loss': -10, 'Max DD': -9, 'Trades': 283}
# snp 500 partial at 15% {'Return %': 59, 'Win Rate': 45, 'Expectancy': 4, 'avg win': 22, 'avg loss': -10, 'Max DD': -15, 'Trades': 334}