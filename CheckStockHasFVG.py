from operator import attrgetter

import yfinance as yf

import AwayFrom52Week
from FVGData import FVGData
from Ticker import *

breakaway = []


def check_good_bullish_fvg(data, ticker):
    bullish_fvg = []

    # print(data)
    for i in range(0, len(data) - 2):
        # print(f"{data['High'].values[i]}")
        # print(f"{data['Low'].values[i+2]}")

        firstCandleHigh = data['High'].values[i]
        thirdCandleLow = data['Low'].values[i + 2]
        thirdCandleHigh = data['High'].values[i + 2]
        secondCandleHigh = data['High'].values[i + 1]
        secondCandleLow = data['Low'].values[i + 1]
        thirdCandleClose = data['Close'].values[i + 2]
        thirdCandleOpen = data['Open'].values[i + 2]
        secondCandleClose = data['Close'].values[i + 1]
        secondCandleOpen = data['Open'].values[i + 1]
        fourthCandleLow = 0

        if i < (len(data) - 3):
            fourthCandleLow = data['Low'].values[i + 3]

        # Check for a bearish candle followed by a bullish candle
        firstCandleHighLessThanThirdCandleLow = firstCandleHigh < thirdCandleLow  # Bearish candle
        firstCandleHighLessThanThirdCandleHigh = firstCandleHigh < thirdCandleHigh  # Bearish candle
        isGoodFVG = True
        # isGoodFVG = secondCandleHigh >= thirdCandleClose and secondCandleHigh >= thirdCandleOpen

        isFVGBroken = (i < (
                len(data) - 3)) and firstCandleHigh > fourthCandleLow  # 4th candle dissrespected the FVG level

        in_consolidation_phase = ((i < (len(data) - 3)) and firstCandleHigh <= fourthCandleLow and
                                  thirdCandleLow >= fourthCandleLow)  # 4th is in between fvg area

        gap = (thirdCandleLow - firstCandleHigh )
        if gap == 0:
            gap = 1
        distance = (gap / (secondCandleClose - secondCandleOpen)) * 100

        # print(f"{distance} distance")
        # bullish_candle = data['Close'].values[i] > data['Open'].values[i]  # Bullish candle

        distanceThreshhold = 5
        stockPrice = stockPriceThreashHold
        broken = False
        if (
                distance > distanceThreshhold and firstCandleHighLessThanThirdCandleHigh and firstCandleHighLessThanThirdCandleLow
                and isFVGBroken):
            broken = True
            print(f"{ticker} disrespected FVG")

        is_consolidating = False
        if (
                distance > distanceThreshhold and firstCandleHighLessThanThirdCandleHigh and firstCandleHighLessThanThirdCandleLow
                and in_consolidation_phase):
            is_consolidating = True
            print(f"{ticker} is consolidating FVG {data.index[i + 1]}")

        if (firstCandleHighLessThanThirdCandleHigh and firstCandleHighLessThanThirdCandleLow
                and firstCandleHigh <= stockPrice and isGoodFVG):
            fvgData = FVGData(data.index[i + 1], ticker, broken, is_consolidating, distance)
            bullish_fvg.append(fvgData)
        elif (firstCandleHighLessThanThirdCandleHigh and firstCandleHighLessThanThirdCandleLow
                and firstCandleHigh <= stockPrice):
            fvgData = FVGData(data.index[i + 1], ticker, broken, is_consolidating, distance)
            breakaway.append(fvgData)



        # if bearish_candle and bullish_candle:
        #     # Check for a gap (Bullish FVG criteria)
        #     gap = data['Low'].values[i] > data['High'].values[i - 1]
        #     # The low of the bullish candle is above the high of the bearish candle
        #
        #     if gap:
        #         bullish_fvg.append(data.index[i])  # Store the index (date) of the bullish FVG

    return bullish_fvg


# Function to determine if there is a bullish FVG
def check_bullish_fvg(data, ticker):
    bullish_fvg = []
    # print(data)
    for i in range(0, len(data) - 2):
        # print(f"{data['High'].values[i]}")
        # print(f"{data['Low'].values[i+2]}")

        firstCandleHigh = data['High'].values[i]
        thirdCandleLow = data['Low'].values[i + 2]
        thirdCandleHigh = data['High'].values[i + 2]
        fourthCandleLow = 0

        if i < (len(data) - 3):
            fourthCandleLow = data['Low'].values[i + 3]

        # Check for a bearish candle followed by a bullish candle
        firstCandleHighLessThanThirdCandleLow = firstCandleHigh < thirdCandleLow  # Bearish candle
        firstCandleHighLessThanThirdCandleHigh = firstCandleHigh < thirdCandleHigh  # Bearish candle

        isFVGBroken = (i < (
                len(data) - 3)) and firstCandleHigh > fourthCandleLow  # 4th candle dissrespected the FVG level

        in_consolidation_phase = ((i < (len(data) - 3)) and firstCandleHigh <= fourthCandleLow and
                                  thirdCandleLow >= fourthCandleLow)  # 4th is in between fvg area

        distance = thirdCandleLow - firstCandleHigh
        # print(f"{distance} distance")
        # bullish_candle = data['Close'].values[i] > data['Open'].values[i]  # Bullish candle

        distanceThreshhold = 5
        stockPrice = stockPriceThreashHold
        broken = False
        if (
                distance > distanceThreshhold and firstCandleHighLessThanThirdCandleHigh and firstCandleHighLessThanThirdCandleLow
                and isFVGBroken):
            broken = True
            print(f"{ticker} disrespected FVG")

        is_consolidating = False
        if (
                distance > distanceThreshhold and firstCandleHighLessThanThirdCandleHigh and firstCandleHighLessThanThirdCandleLow
                and in_consolidation_phase):
            is_consolidating = True
            print(f"{ticker} is consolidating FVG data.index[i+1]")

        if (
                distance > distanceThreshhold and firstCandleHighLessThanThirdCandleHigh and firstCandleHighLessThanThirdCandleLow
                and firstCandleHigh <= stockPrice):
            fvgData = FVGData(data.index[i + 1], ticker, broken, is_consolidating, distance)
            bullish_fvg.append(fvgData)

        # if bearish_candle and bullish_candle:
        #     # Check for a gap (Bullish FVG criteria)
        #     gap = data['Low'].values[i] > data['High'].values[i - 1]
        #     # The low of the bullish candle is above the high of the bearish candle
        #
        #     if gap:
        #         bullish_fvg.append(data.index[i])  # Store the index (date) of the bullish FVG

    return bullish_fvg


# Function to determine if there is a bullish FVG
def check_stock_has_bearish_fvg(data, ticker):
    bullish_fvg = []
    # print(data)
    for i in range(0, len(data) - 2):
        # print(f"{data['High'].values[i]}")
        # print(f"{data['Low'].values[i+2]}")

        firstCandleLow = data['Low'].values[i]
        firstCandleHigh = data['High'].values[i]
        thirdCandleLow = data['Low'].values[i + 2]
        thirdCandleHigh = data['High'].values[i + 2]
        fourthCandleLow = 0

        if i < (len(data) - 3):
            fourthCandleLow = data['Low'].values[i + 3]

        firstCandleLowGreaterThanThirdCandleLow = firstCandleLow > thirdCandleLow
        firstCandleHighGreaterThanThirdCandleHigh = firstCandleHigh > thirdCandleHigh
        firstCandleLowGreaterThanThirdCandleHigh = firstCandleLow > thirdCandleHigh

        distance = firstCandleLow - thirdCandleHigh
        # print(f"{distance} distance")
        # bullish_candle = data['Close'].values[i] > data['Open'].values[i]  # Bullish candle

        distanceThreshhold = 5
        stockPrice = stockPriceThreashHold

        if (distance > distanceThreshhold
                and firstCandleLowGreaterThanThirdCandleLow
                and firstCandleHighGreaterThanThirdCandleHigh
                and firstCandleLowGreaterThanThirdCandleHigh
                and firstCandleHigh <= stockPrice):
            fvgData = FVGData(data.index[i + 1], ticker, False, False, distance)
            bullish_fvg.append(fvgData)

    return bullish_fvg


# Function to fetch data and check bullish FVG for a list of tickers
def analyze_stocks_daily_fvg(tickers1, time, checkGoodFVG, trend, startTime, endTime):
    fvg_stock_list = []
    no_fvg_stock_list = []
    print(f"Start date and time: {startTime}")
    print(f"End date and time: {endTime}")
    for ticker in tickers1:
        print(f"Analyzing {ticker}...")
        # Fetch stock data from Yahoo Finance
        data = yf.download(ticker, startTime, endTime, interval=time)
        # print(f"Analyzing {data}...")

        if trend == "bull":
            # Check for bullish FVGs
            if checkGoodFVG:
                bullish_fvgs = check_good_bullish_fvg(data, ticker)
            else:
                bullish_fvgs = check_bullish_fvg(data, ticker)
        else:
            bullish_fvgs = check_stock_has_bearish_fvg(data, ticker)

        # Print the results
        if bullish_fvgs:
            print(f" {len(bullish_fvgs)} Daily Bullish FVGs detected for {ticker} on the following dates:")
            bullish_fvgs[0].set_count(len(bullish_fvgs))
            stock_info = AwayFrom52Week.percentage_difference_52_week_high(ticker)
            if stock_info:
                bullish_fvgs[0].set_away_from52_week_high(stock_info.awayFrom52W)
            if stock_info.institutionPercent is not None:
                bullish_fvgs[0].set_institution_holding(stock_info.institutionPercent)
            fvg_stock_list.append(bullish_fvgs[0])
            for fvg in bullish_fvgs:
                print(fvg.date.strftime('%Y-%m-%d'))
        else:
            no_fvg_stock_list.append(ticker)
            # print(f"")
            # print(f"No Bullish FVGs detected for {ticker}.")
        # print("=" * 40)

    # Sort by awayFromHigh
    sorted_fvg = sorted(fvg_stock_list, key=attrgetter('awayFrom52WeekHigh'))
    # print(sorted_fvg)

    ticker_for_hrly_fvg = []
    for fvg in sorted_fvg:
        ticker_for_hrly_fvg.append(fvg.get_name())

    hourly_fvg = []
    if time == "1d":
        hourly_fvg = analyze_stocks_daily_fvg(ticker_for_hrly_fvg, "15m", False, trend, startHr, endHr)
        print(f" breakaway daily gaps fvg_stock_list")
        for fvg in breakaway:
            fvg.print()

    print(f"{time} fvg_stock_list")
    for fvg in fvg_stock_list:
        fvg.printData()

    print(f" hourly/ 15 m fvg_stock_list")
    for fvg in hourly_fvg:
        fvg.printData()

    print(f" breakaway {time} gaps fvg_stock_list")
    for fvg in breakaway:
        fvg.printData()

    return sorted_fvg


# Function to fetch data and check bullish FVG for a list of tickers
def analyze_stocks_weekly_fvg(tickers1, checkGoodFVG, trend, startTime, endTime):
    wfvg_stock_list = []
    no_fvg_stock_list = []
    for ticker in tickers1:
        # print(f"Analyzing {ticker}...")
        # Fetch stock data from Yahoo Finance
        data = yf.download(ticker, startTime, endTime, interval="1wk")

        if trend == "bull":
            # Check for bullish FVGs
            if checkGoodFVG:
                bullish_fvgs = check_good_bullish_fvg(data, ticker)
            else:
                bullish_fvgs = check_bullish_fvg(data, ticker)
        else:
            bullish_fvgs = check_stock_has_bearish_fvg(data, ticker)

        # Print the results
        if bullish_fvgs:
            print(f" {len(bullish_fvgs)} Bullish FVGs detected for {ticker} on the following dates:")
            wfvg_stock_list.append(ticker)
            for date in bullish_fvgs:
                print(date.date.strftime('%Y-%m-%d'))

            # print(f"")
            # print(f"No Bullish FVGs detected for {ticker}.")
        # print("=" * 40)

    analyze_stocks_daily_fvg(wfvg_stock_list, "1d", True, trend, startDaily, endDaily)

    print(f" WEEKLY fvg_stock_list")
    for fvg in wfvg_stock_list:
        print(fvg)


stockPriceThreashHold = 15000

# analyze_stocks_weekly_fvg(get_tickers("ALL"), checkGoodFVG=True, trend="bull")

# # Analyze the stocks
# analyze_stocks_daily_fvg(get_tickers("ALL"), "1d", checkGoodFVG=True,
#                          trend="bull", startTime=startDaily, endTime=startDaily)


# brearish daily
# analyze_stocks_daily_fvg(get_tickers("MINE"), "4h", checkGoodFVG=True,
#                          trend="bull", startTime="2025-01-06", endTime="2025-01-13")
