import yfinance as yf


class StockInfo:
    def __init__(self, institutionPercent, awayFrom52W):
        self.institutionPercent = institutionPercent
        self.awayFrom52W = awayFrom52W


def percentage_difference_52_week_high(ticker_symbol):
    """
    Calculate the percentage difference between the current price of a stock
    and its 52-week high.

    Args:
        ticker_symbol (str): The ticker symbol of the stock (e.g., "RELIANCE.NS" for Reliance Industries).

    Returns:
        StockInfo: The percentage difference.
    """
    try:
        # Fetch stock data
        stock = yf.Ticker(ticker_symbol)
        stock_info = stock.info
        # print(stock_info)

        # Extract the 52-week high and current price
        week_high_52 = stock_info.get('fiftyTwoWeekHigh')
        current_price = stock_info.get('currentPrice')
        held_percent_institutions = stock_info.get('heldPercentInstitutions')

        # Check if data is available
        if week_high_52 is None or current_price is None:
            raise ValueError("Unable to retrieve stock data.")

        # Calculate percentage difference
        percentage_difference = ((week_high_52 - current_price) / week_high_52)
        held_percent_institutions = held_percent_institutions
        print(f"diff  {percentage_difference}  {held_percent_institutions}")
        return StockInfo(percentage_difference, held_percent_institutions)

    except Exception as e:
        print(f"ticker_symbol no data away from Error: {e}")
        return StockInfo(0, 0)


ticker = "TRANSRAILL.NS"  # Replace with the Indian stock ticker symbol
result: StockInfo = percentage_difference_52_week_high(ticker)
if result is not None:
    print(f"The percentage difference from the 52-week high for {ticker} is ")