# Based on the date range, will give a history of dividend and total payout till date.

import yfinance as yf
import sys

# Get the command line arguments
args = sys.argv

total = 0

def convert_timestamp(timestamp):
    return timestamp.strftime('%Y-%m-%d')

def get_historical_ex_dividends(ticker):
    # Download the stock data using yfinance
    stock = yf.Ticker(ticker)
    global total

    # Fetch dividend history (dividend payments)
    dividends = stock.dividends  # This gives a pandas Series of dividend payments with dates

    if dividends.empty:
        print(f"No dividend history available for {ticker.upper()}")
        return

    # Fetch ex-dividend dates and payment amounts from dividend payment history
    ex_dividend_dates = dividends.index  # Dates of the dividend payments
    payment_amounts = dividends.values  # Corresponding payment amounts

    # Convert the dates to human-readable format
    ex_dividend_dates = [convert_timestamp(date) for date in ex_dividend_dates]

    # Output the historical ex-dividend dates and payment amounts
    print(f"Historical Ex-Dividend Dates for {ticker.upper()}:")
    for date, amount in zip(ex_dividend_dates, payment_amounts):
        print(f"Date: {date}, Payment Amount: ${amount:.3f}")
        total += amount

# Example usage
# get_historical_ex_dividends('AAPL')
        

# Example usage
# ticker_symbol = 'MSTY'  # You can change this to any other stock ticker symbol
ticker_symbol = args[1]
get_historical_ex_dividends(ticker_symbol)
print(f"Total payments: {total:.3f}")
