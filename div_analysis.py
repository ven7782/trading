# Analyze any ticker symbol for performance till date
# Define the date range below and make a csv file with Column symbol and the ticker symbols.
# Provides 3 columns. Gain if div was reinvested back to stocks, gain if div was kept in cash, total div for date range
# Output csv file has _performance_analysis.csv name

import yfinance as yf
import pandas as pd
from datetime import datetime
import os

# Load the CSV file into a DataFrame (assuming your CSV has a column named 'Symbol')
file = 'Yield_max.csv'  # Replace with your actual CSV file path
tickers_df = pd.read_csv(file)

# Define the dates for analysis
start_date = '2024-01-01'  # First trading day of year
end_date = '2024-10-11'    # Today's trading date, whatever that is

# Function to analyze performance for a single ticker symbol
def analyze_ticker_performance(ticker):
    # try:
    # Download stock data using yfinance
    share = yf.Ticker(ticker)
    stock = yf.download(ticker, start=start_date)

    # Get historical price data
    # hist = stock.history(start=start_date, end=end_date)

    # Extract the first adjusted close of 2023 and adjusted close of 10/9/2024
    adjusted_close_start = stock['Adj Close'].iloc[0]
    # adjusted_close_end = stock['Adj Close'].loc[end_date]
    adjusted_close_end = stock['Adj Close'].iloc[-1]

    # Adjusted Close strategy percentage increase
    adjusted_close_percentage_increase = (adjusted_close_end / adjusted_close_start - 1) * 100

    # Extract the first close of start and the close of end date
    close_start = stock['Close'].iloc[0]
    close_end = stock['Close'].iloc[-1]

    # Get total dividends paid between start and end date
    dividends = share.dividends
    dividends_start_end = dividends[(dividends.index >= start_date) & (dividends.index <= end_date)].sum()

    # Close price strategy: Add dividends paid to the close price of end date
    total_value_close_strategy = close_end + dividends_start_end
    close_price_percentage_increase = (total_value_close_strategy / close_start - 1) * 100

    # Return both percentage increases
    return {
        'Adjusted Close % Gain': round(adjusted_close_percentage_increase, 2),
        'Close Price + Dividends % Gain': round(close_price_percentage_increase, 2),
        'Total div': dividends_start_end
    }

    # except Exception as e:
    #     print(f"Error analyzing {ticker}: {e}")
    #     return None

# Analyze each ticker and store results
results = []
for index, row in tickers_df.iterrows():
    ticker = row['Symbol']
    # Mkt_Cap = row['Mkt Cap']
    print(f"Analyzing {ticker}...")
    result = analyze_ticker_performance(ticker)
    if result:
        results.append({
            'Ticker': ticker,
            # 'Mkt Cap': Mkt_Cap,
            'Div_Reinvest % Gain': result['Adjusted Close % Gain'],
            'Cash_Div % gain': result['Close Price + Dividends % Gain'],
            'Total div': result['Total div']
        })

# Convert results to DataFrame and save to CSV
results_df = pd.DataFrame(results)
output_file = os.path.splitext(os.path.basename(file))[0] + "_performance_analysis.csv"
# output_file = 'performance_analysis_results.csv'  # Set the output file path
results_df.to_csv(output_file, index=False)

print(f"Analysis complete. Results saved to {output_file}")
