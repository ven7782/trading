import yfinance as yf
from datetime import datetime

# Function to convert Unix timestamp to human-readable date
def convert_timestamp(timestamp):
    if timestamp is not None:
        return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d')
    else:
        return "No data available"

# Function to get stock data
def get_stock_data(ticker):
    # Download the stock data using yfinance
    stock = yf.Ticker(ticker)
    # print(stock.dividends)

    # Fetch earnings date
    earnings_dates = stock.earnings_dates
    if earnings_dates is not None and not earnings_dates.empty:
        next_earnings_date = earnings_dates.index[0]  # Get the next earnings date
    else:
        next_earnings_date = "No data available"

    # Fetch forward dividend and yield
    forward_dividend = stock.info.get("dividendRate", "No data available")
    dividend_yield = stock.info.get("dividendYield", "No data available")
    
    # Fetch ex-dividend date and convert Unix timestamp to human-readable format
    ex_dividend_timestamp = stock.info.get("exDividendDate", None)
    ex_dividend_date = convert_timestamp(ex_dividend_timestamp)

    # Format the dividend yield as a percentage if available
    if dividend_yield != "No data available":
        dividend_yield = f"{dividend_yield * 100:.2f}%"

    # Output the information
    print(f"Stock: {ticker.upper()}")
    print(f"Earnings Date: {next_earnings_date}")
    print(f"Forward Dividend: {forward_dividend}")
    print(f"Dividend Yield: {dividend_yield}")
    print(f"Ex-Dividend Date: {ex_dividend_date}")

# Example usage
ticker_symbol = 'VZ'  # You can change this to any other stock ticker symbol
get_stock_data(ticker_symbol)
