# Calculate support and resistance level till date.
# Adjust the date range to calculate the same for a specific duration

import yfinance as yf
import pandas as pd
import numpy as np
import sys
import talib

# talib is a technical analysis library.
# TA_LIB: https://github.com/cgohlke/talib-build/releases
# https://github.com/ta-lib/ta-lib-python

# Get the command line arguments
args = sys.argv

# Fetch historical data for ASML
ticker = args[1]
data = yf.download(ticker)
print(data)
# data = yf.download(ticker, start="2020-01-01", end="2024-10-15")

# Calculate the support and resistance levels
def calculate_support_resistance(data):
    # Calculate rolling max and min for 20 days
    data['20_day_high'] = data['High'].rolling(window=20).max()
    data['20_day_low'] = data['Low'].rolling(window=20).min()
    data['RSI'] = talib.RSI(data['Close'])

    # The most recent high and low from the 20-day rolling window
    latest_high = data['20_day_high'].iloc[-1]
    latest_low = data['20_day_low'].iloc[-1]
    RSI = data['RSI'].iloc[-1]

    return latest_low, latest_high, RSI

support, resistance, rsi = calculate_support_resistance(data)

print(f"Support Level: {support}")
print(f"Resistance Level: {resistance}")
print(f"RSI: {rsi}")