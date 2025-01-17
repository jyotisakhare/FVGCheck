from CheckStockHasFVG import analyze_stocks_daily_fvg, analyze_stocks_weekly_fvg
from Ticker import *


def switch_menu():
    while True:
        print("\nSelect an operation:")
        print("1. Daily GFVG")
        print("2. Weekly GFVG")
        print("3. Montly GFVG")
        print("4. Bearish Daily RFVG")
        print("5. Bearish Weekly RFVG")
        print("6. Hourly bull FVG")

        choice = input("Enter your choice (1-5): ")

        match choice:
            case "1":
                analyze_stocks_daily_fvg(get_tickers(tickerGroup), "1d", checkGoodFVG=isGoodFVG,
                                         trend="bull", startTime=startDaily, endTime=endDaily)
                break
            case "2":
                analyze_stocks_weekly_fvg(get_tickers(tickerGroup), checkGoodFVG=isGoodFVG,
                                          trend="bull", startTime=startW, endTime=endW)
                break
            case "3":
                analyze_stocks_daily_fvg(get_tickers(tickerGroup), "1mo", checkGoodFVG=False,
                                         trend="bull", startTime=startM, endTime=endM)
                break
            case "4":
                analyze_stocks_daily_fvg(get_tickers(tickerGroup), "1d", checkGoodFVG=False,
                                         trend="bear", startTime=startDaily, endTime=endDaily)
                break
            case "5":
                analyze_stocks_daily_fvg(get_tickers(tickerGroup), "1wk", checkGoodFVG=False,
                                         trend="bear", startTime=startW, endTime=endW)
                break
            case "6":
                analyze_stocks_daily_fvg(get_tickers(tickerGroup), "1h", checkGoodFVG=False,
                                         trend="bull", startTime=startHr, endTime=endHr)
                break
            case "7":
                print("Exiting the program. Goodbye!")
                break
            case _:
                print("Invalid choice. Please try again.")


if __name__ == "__main__":
    switch_menu()
