from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional, Tuple

import pandas as pd

# pip install yfinance pandas
import yfinance as yf

from Ticker import tickerGroup, get_tickers


@dataclass
class StockScanResult:
    ticker: str
    close: float
    ema200: float
    crossed_ema200: bool
    high_52w: float
    pct_from_52w_high: float


def _compute_ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False).mean()


def scan_stocks(
    tickers: Iterable[str],
    *,
    ema_span: int = 200,
    high_lookback_trading_days: int = 252,   # ~52 weeks
    near_high_within_pct: float = 5.0,       # within 5%
    history_period: str = "2y",              # enough data for 200 EMA + 52w high
) -> Tuple[List[str], pd.DataFrame]:
    """
    Returns:
      - list of tickers that crossed above 200 EMA AND are within near_high_within_pct of 52w high
      - dataframe with metrics for all tickers successfully processed
    """
    tickers = [t.strip().upper() for t in tickers if str(t).strip()]
    if not tickers:
        return [], pd.DataFrame()

    results: List[StockScanResult] = []

    # Download in one shot for speed; group by ticker
    data = yf.download(
        tickers=tickers,
        period=history_period,
        interval="1d",
        auto_adjust=False,
        group_by="ticker",
        threads=True,
        progress=False,
    )

    def get_close_df(ticker: str) -> Optional[pd.Series]:
        # yfinance shape differs for 1 vs many tickers
        if isinstance(data.columns, pd.MultiIndex):
            if ticker not in data.columns.get_level_values(0):
                return None
            return data[(ticker, "Close")].dropna()
        else:
            # single ticker case
            if "Close" not in data.columns:
                return None
            return data["Close"].dropna()

    for t in tickers:
        close = get_close_df(t)
        if close is None or len(close) < max(ema_span + 5, high_lookback_trading_days):
            continue

        ema200 = _compute_ema(close, ema_span)

        # Crossed above today: yesterday close < yesterday EMA AND today close > today EMA
        # crossed = bool(
        #     close.iloc[-2] < ema200.iloc[-2] and close.iloc[-1] > ema200.iloc[-1]
        # )
        crossed = bool(close.iloc[-1] > ema200.iloc[-1])

        # 52-week high from last ~252 trading days (including today)
        window = close.iloc[-high_lookback_trading_days:]
        high_52w = float(window.max())

        last_close = float(close.iloc[-1])
        pct_from_high = (high_52w - last_close) / high_52w * 100.0  # 0% means at the high

        near_high = pct_from_high <= near_high_within_pct

        results.append(
            StockScanResult(
                ticker=t,
                close=last_close,
                ema200=float(ema200.iloc[-1]),
                crossed_ema200=crossed,
                high_52w=high_52w,
                pct_from_52w_high=float(pct_from_high),
            )
        )

    df = pd.DataFrame([r.__dict__ for r in results])
    if df.empty:
        return [], df

    # Filter: crossed + near high
    picks = df[(df["crossed_ema200"]) & (df["pct_from_52w_high"] <= near_high_within_pct)].copy()

    # Nice sorting: closest to 52w high first
    picks = picks.sort_values(["pct_from_52w_high", "ticker"], ascending=[True, True])

    return picks["ticker"].tolist(), picks.reset_index(drop=True)


# Shashank udupa 200 EMA crossing strategy for swing trading
# https://chartink.com/screener/within-2-of-52-week-highs-chartitude
#
#
# 1 ATH
# 2 cross 200 EMA - and gains with high momentum within 90 days and breaks the ATH
# 3. Breaks ATH - enter here and exist when it touch 200 EMA again
# Stage 2 analysis  - plus the above https://chartink.com/screener/stage-2-trend-template

if __name__ == "__main__":
    input_tickers = get_tickers(tickerGroup)  # <-- your list
    selected, details = scan_stocks(input_tickers)

    print("Selected tickers:", selected)
    print(details.to_string(index=False))
