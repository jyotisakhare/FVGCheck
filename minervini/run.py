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
            cfg["TOP_N"] = 1

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

# India results till 6th MAY
# normal
# {'Return %': 27, 'Win Rate': 54, 'Expectancy': 6, 'avg win': 19, 'avg loss': -9, 'Max DD': -9, 'Trades': 80}
# {'Return %': 29, 'Win Rate': 54, 'Expectancy': 6, 'avg win': 19, 'avg loss': -9, 'Max DD': -9, 'Trades': 80} 24 may minervini
# {'Return %': 33, 'Win Rate': 64, 'Expectancy': 5, 'avg win': 13, 'avg loss': -9, 'Max DD': -6, 'Trades': 102} 200 EMA
# 20 trades at a time with 200 EMA
# {'Return %': 42, 'Win Rate': 58, 'Expectancy': 5, 'avg win': 15, 'avg loss': -10, 'Max DD': -7, 'Trades': 180}
# 20 trades at a time 220 EMA exit whit 20 EMA touched
# {'Return %': 43, 'Win Rate': 59, 'Expectancy': 4, 'avg win': 13, 'avg loss': -10, 'Max DD': -8, 'Trades': 222}
# {'Return %': 62, 'Win Rate': 53, 'Expectancy': 4, 'avg win': 16, 'avg loss': -10, 'Max DD': -12, 'Trades': 200} 5 year 200 EMA

# US results till 20th APR
# {'Return %': 35, 'Win Rate': 48, 'Expectancy': 5, 'avg win': 22, 'avg loss': -11, 'Max DD': -14, 'Trades': 122}
# TOP 2 27 may
# {'Return %': 33, 'Win Rate': 48, 'Expectancy': 5, 'avg win': 22, 'avg loss': -11, 'Max DD': -13, 'Trades': 126}
# 200 EMA top 2 with max 20 trades
#  {'Return %': 49, 'Win Rate': 57, 'Expectancy': 6, 'avg win': 19, 'avg loss': -10, 'Max DD': -11, 'Trades': 165}