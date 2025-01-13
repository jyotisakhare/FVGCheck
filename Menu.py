from CheckStockHasFVG import analyze_stocks_daily_fvg, analyze_stocks_weekly_fvg
from Ticker import get_tickers

startDaily = "2025-01-01"
endDaily = "2025-01-10"

startHr = "2025-01-10"
endHr = "2025-01-13"

stockPriceThreashHold = 15000

startW = "2024-12-17"
endW = "2025-01-20"

startM = "2024-10-01"
endM = "2025-01-31"

isGoodFVG = True
tickerGroup = "MINE"


def switch_menu():
    while True:
        print("\nSelect an operation:")
        print("1. Daily GFVG")
        print("2. Weekly GFVG")
        print("3. Montly GFVG")
        print("4. Daily RFVG")
        print("5. Weekly RFVG")

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
                analyze_stocks_daily_fvg(get_tickers(tickerGroup), "1mo", checkGoodFVG=isGoodFVG,
                                         trend="bull", startTime=startM, endTime=endM)
                break
            case "4":
                analyze_stocks_daily_fvg(get_tickers(tickerGroup), "1d", checkGoodFVG=isGoodFVG,
                                         trend="bear", startTime=startDaily, endTime=endDaily)
                break
            case "5":
                print("Exiting the program. Goodbye!")
                break
            case _:
                print("Invalid choice. Please try again.")


if __name__ == "__main__":
    switch_menu()
