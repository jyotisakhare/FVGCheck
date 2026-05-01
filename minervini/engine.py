from portfolio import Portfolio
from strategy import check_entry
from features import calculate_score


def run_backtest(data, cfg):

    portfolio = Portfolio(cfg["INITIAL_CAPITAL"], cfg)
    trades = []
    equity = []

    # Unified timeline
    all_dates = sorted(set().union(*[df.index for df in data.values()]))

    for date in all_dates:

        # ================= EXIT =================
        for symbol in list(portfolio.positions.keys()):

            df = data.get(symbol)
            if df is None or date not in df.index:
                continue

            i = df.index.get_loc(date)

            # cannot exit on last candle (no next open)
            if i + 1 >= len(df):
                continue

            row = df.iloc[i]

            portfolio.update(symbol, row)

            exit_flag, exit_reason = portfolio.check_exit(symbol, row, i, cfg, df)
            if exit_flag:

                next_open = df.iloc[i + 1]["Open"]
                pos = portfolio.positions[symbol]

                # safety check
                if next_open is None or next_open <= 0:
                    continue

                # update capital
                portfolio.capital += pos["shares"] * next_open

                trades.append({
                    "Symbol": symbol,
                    "Entry Date": pos["entry_date"],
                    "Exit Date": df.index[i + 1],
                    "Entry Price": pos["entry"],
                    "Exit Price": next_open,
                    "Return %": (next_open - pos["entry"]) / pos["entry"] * 100,
                    "reason": exit_reason
                })

                del portfolio.positions[symbol]

        # ================= ENTRY =================
        candidates = []

        for symbol, df in data.items():

            if symbol in portfolio.positions:
                continue

            if date not in df.index:
                continue

            i = df.index.get_loc(date)

            # need enough history + next candle
            if i < 300 or i + 1 >= len(df):
                continue

            try:
                if check_entry(df, i, cfg, symbol, debug=False):
                    score = calculate_score(df, i)

                    # skip bad scores
                    if score is None:
                        continue


                    candidates.append((symbol, score, i))

            except Exception as e:
                # skip bad data silently
                print(e)
                print(repr(e))
                continue

        # ===== DEBUG (optional) =====
        print(f"{date} → candidates: {len(candidates)}")

        # ================= RANK =================
        candidates.sort(key=lambda x: x[1], reverse=True)

        # ================= POSITION CONTROL =================
        slots_available = cfg["MAX_POSITIONS"] - len(portfolio.positions)

        if slots_available > 0:

            selected = candidates[:min(cfg["TOP_N"], slots_available)]

            for symbol, score, i in selected:

                df = data[symbol]

                entry_price = df.iloc[i + 1]["Open"]
                entry_date = df.index[i + 1]

                # safety check
                if entry_price is None or entry_price <= 0:
                    continue

                portfolio.enter(symbol, entry_price, entry_date, i + 1)

        # ================= EQUITY =================
        total_equity = portfolio.capital

        for s, pos in portfolio.positions.items():

            df = data.get(s)

            if df is None or date not in df.index:
                continue

            close_price = df.loc[date]["Close"]

            if close_price is None or close_price <= 0:
                continue

            total_equity += pos["shares"] * close_price

        equity.append({
            "Date": date,
            "Equity": total_equity
        })

    return trades, equity