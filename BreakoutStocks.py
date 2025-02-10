import yfinance as yf
import pandas as pd
import numpy as np
from yfinance import Ticker

from FVGData import FVGData
from Ticker import get_tickers


def get_rsi(data, window=14):
    """Calculate Relative Strength Index (RSI)"""
    delta = data["Close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


def get_macd(data, short_window=12, long_window=26, signal_window=9):
    """Calculate MACD and Signal Line"""
    short_ema = data["Close"].ewm(span=short_window, adjust=False).mean()
    long_ema = data["Close"].ewm(span=long_window, adjust=False).mean()
    data["MACD"] = short_ema - long_ema
    data["MACD_Signal"] = data["MACD"].ewm(span=signal_window, adjust=False).mean()
    return data


def get_bollinger_bands(data, window=20, std_dev=2):
    """Calculate Bollinger Bands"""
    data["Middle_Band"] = data["Close"].rolling(window=window).mean()
    data["Upper_Band"] = data["Middle_Band"] + (std_dev * data["Close"].rolling(window=window).std())
    data["Lower_Band"] = data["Middle_Band"] - (std_dev * data["Close"].rolling(window=window).std())
    return data


breakout_vol = []
breakout_price = []
breakout_rsi = []
breakout_macd = []


def get_breakout_stocks(stock_list, lookback=50, volume_multiplier=1.5, rsi_threshold=60):
    breakout_stocks = []

    for ticker in stock_list:
        try:
            # Fetch last 60 days of stock data
            stock_data = yf.download(ticker, period="3mo", interval="1d")
            # print(stock_data)
            # Calculate Indicators
            stock_data["50d_High"] = stock_data["High"].rolling(window=lookback).max()
            stock_data["RSI"] = get_rsi(stock_data)
            stock_data["Avg_Vol"] = stock_data["Volume"].rolling(window=50).mean()
            stock_data = get_macd(stock_data)
            # stock_data = get_bollinger_bands(stock_data)

            # Get latest data points
            latest_data = stock_data.iloc[-1]
            prev_data = stock_data.iloc[-2]  # Previous day's data for confirmation
            latest_data_close = latest_data["Close"].reset_index(drop=True)
            prev_data_close = prev_data["Close"].reset_index(drop=True)
            # print("here1")
            # print(stock_data.iloc[-1])

            # Conditions for a strong breakout
            price_breakout = (latest_data_close > latest_data["50d_High"].reset_index(drop=True)) & (prev_data_close <= prev_data["50d_High"].reset_index(drop=True))

            # print("latest_data[Volume]", latest_data["Volume"].reset_index(drop=True))
            latest_data_vol = latest_data["Volume"].reset_index(drop=True)
            volume_spike = latest_data_vol > (volume_multiplier * latest_data["Avg_Vol"].reset_index(drop=True))

            rsi_confirm = latest_data["RSI"].reset_index(drop=True) > rsi_threshold

            macd_confirm = latest_data["MACD"].reset_index(drop=True) > latest_data["MACD_Signal"].reset_index(drop=True)  # Bullish MACD crossover

            # bollinger_confirm = latest_data["Close"] > latest_data["Upper_Band"]  # Price breaking upper Bollinger Band

            # if price_breakout and volume_spike and rsi_confirm and macd_confirm and bollinger_confirm:
            #     breakout_stocks.append(ticker)
            # print("here3.5", price_breakout)
            # print("here4")
            # if price_breakout.any() & volume_spike.any():
            #     breakout_stocks.append(ticker)
            fvg = FVGData(ticker, 0)
            # print("here5")
            if price_breakout.any():
                print("price_breakout", ticker)
                fvg.increment_rank()
                breakout_price.append(ticker)
            if volume_spike.any():
                fvg.increment_rank()
                print("volume_spike", ticker)
                breakout_vol.append(ticker)
            if rsi_confirm.any():
                fvg.increment_rank()
                print("rsi", ticker)
                breakout_rsi.append(ticker)
            if macd_confirm.any():
                fvg.increment_rank()
                print("macd", ticker)
                breakout_macd.append(ticker)

            if fvg.rank > 0:
                breakout_stocks.append(fvg)

        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")

    return breakout_stocks


def sort_fvg_data(s):
    return s.rank


# Run the scanner
breakout_stocks_list = get_breakout_stocks(get_tickers("MINE"))
sorted_list = sorted(breakout_stocks_list, key=sort_fvg_data, reverse=True)
print("Stocks with a strong breakout:")
for fvg in sorted_list:
    fvg.printNameAndRank()
print("Stocks with a strong vol breakout:", breakout_vol.sort())
print("Stocks with a strong price breakout:", breakout_price.sort())
print("Stocks with a strong rsi breakout:", breakout_rsi.sort())
print("Stocks with a strong macd breakout:", breakout_macd.sort())
