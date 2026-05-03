# metrics.py

import pandas as pd
from config import CONFIG

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

    if CONFIG["MARKET"] == "INDIA":
        trades.to_csv("trades_ind.csv", index=False)
        equity.to_csv("equity_ind.csv", index=False)
    else:
        trades.to_csv("trades_us.csv", index=False)
        equity.to_csv("equity_us.csv", index=False)

    return {
        "Return %": round(total_return),
        "Win Rate": round(win_rate),
        "Expectancy": round(expectancy),
        "avg win": round(avg_win),
        "avg loss": round(avg_loss),
        "Max DD": round(max_dd),
        "Trades": len(trades)
    }