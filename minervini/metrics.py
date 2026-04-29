# metrics.py

import numpy as np

import pandas as pd

def compute_metrics(trades, equity, initial):

    if len(trades) == 0 or len(equity) == 0:
        return {}

    trades = pd.DataFrame(trades)
    equity = pd.DataFrame(equity)

    # ===== RETURNS =====
    final_equity = equity["Equity"].iloc[-1]
    total_return = (final_equity - initial) / initial * 100

    # ===== WIN / LOSS =====
    wins = trades[trades["Return %"] > 0]
    losses = trades[trades["Return %"] <= 0]

    win_rate = len(wins) / len(trades) * 100 if len(trades) > 0 else 0

    avg_win = wins["Return %"].mean() if len(wins) > 0 else 0
    avg_loss = losses["Return %"].mean() if len(losses) > 0 else 0

    # ===== EXPECTANCY (CORRECT) =====
    expectancy = (win_rate/100 * avg_win) + ((1 - win_rate/100) * avg_loss)

    # ===== DRAWDOWN =====
    equity["Peak"] = equity["Equity"].cummax()
    equity["DD"] = (equity["Equity"] - equity["Peak"]) / equity["Peak"]

    max_dd = equity["DD"].min() * 100

    return {
        "Return %": total_return,
        "Win Rate": win_rate,
        "Expectancy": expectancy,
        "avg win": avg_win,
        "avg loss": avg_loss,
        "Max DD": max_dd,
        "Trades": len(trades)
    }