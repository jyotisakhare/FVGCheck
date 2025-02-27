import yfinance as yf
import numpy as np

from Ticker import get_tickers


def get_vcp_contractions(stock_symbols):
    contractions = {}

    for symbol in stock_symbols:
        stock = yf.Ticker(symbol)
        # print(f"checking {symbol}")
        data = stock.history(period="1mo", interval="1d")  # Fetch last 12 weeks of data
        # print(data)
        if len(data) < 3:
            print(f"Not enough data for {symbol}")
            continue

        data = data.tail(5)  # Ensure only last 3 weeks are considered
        # print(data)
        # Calculate range (close - open)
        data['Range'] = data['Close'] - data['Open']
        # Check if the ranges are contracting
        ranges = data['Range'].values
        highs = data['High'].values
        lows = data['Low'].values

        contraction = all(ranges[i] >= ranges[i + 1] for i in range(len(ranges) - 1))

        if contraction:
            print(f"{symbol}: {ranges}")
            contractions[symbol] = list(ranges)

        # contractionh = all(highs[i] >= highs[i + 1] for i in range(len(ranges) - 1))
        # contractionl = all(lows[i] >= lows[i + 1] for i in range(len(ranges) - 1))
        #
        # if contractionl and contractionh:
        #     print(f" mine {symbol}: {ranges}")
        #     contractions[symbol] = list(ranges)

    return contractions


# Example usage
stock_list = ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA"]  # Replace with Indian stocks if needed
vcp_stocks = get_vcp_contractions(get_tickers("MINE"))

print("Stocks showing VCP contraction in the last 5 days:")
for stock, ranges in vcp_stocks.items():
    print(f"{stock}: {ranges}")
