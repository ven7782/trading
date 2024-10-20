'''Example Chain-of-Thought Prompt for Financial Analysis:
Analyze the company's income statement, balance sheet, and cash flow statement step by step. First, examine revenue, cost of goods sold, and operating expenses over the last 5 quarters. How have these metrics changed quarter over quarter? Next, evaluate profitability indicators such as gross margin, operating margin, and net income. After that, analyze cash flow from operations and capital expenditures to assess liquidity. Finally, consider external risks mentioned in the MD&A, such as competition or regulatory challenges. Based on all these factors, forecast whether the company's EPS will increase or decrease next quarter, and explain your reasoning.'''

import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd
pd.set_option('display.max_rows', None)

#financials, quarterly_financials, balance_sheet, quarterly_balance_sheet, cashflow, quarterly_cashflow, earnings, quarterly_earnings

def get_financial_data(ticker_symbol):
    # Download financial data using yfinance
    ticker = yf.Ticker(ticker_symbol)
    
    # Get the past 4 years of data (quarterly)
    income_statement = ticker.financials  # Transpose the dataframe
    balance_sheet = ticker.balance_sheet
    cash_flow = ticker.cashflow

    # Filter the past 4 years (quarterly data)
    # four_years_ago = datetime.now() - timedelta(days=4*365)
    
    # Filtering the data for the past 4 years
    # income_statement_filtered = income_statement[income_statement.index >= four_years_ago.strftime('%Y-%m-%d')]
    # balance_sheet_filtered = balance_sheet[balance_sheet.index >= four_years_ago.strftime('%Y-%m-%d')]
    # cash_flow_filtered = cash_flow[cash_flow.index >= four_years_ago.strftime('%Y-%m-%d')]
    
    return pd.DataFrame(income_statement), pd.DataFrame(balance_sheet), pd.DataFrame(cash_flow)

# Usage
ticker_symbol = "NFLX"  # Replace with the desired ticker symbol
income_statement, quarterly_balance_sheet, cash_flow = get_financial_data(ticker_symbol)

# Display the filtered data
print("Income Statement (last 4 years):")
print(income_statement)

print("\nBalance Sheet (last 4 years):")
print(quarterly_balance_sheet)

print("\nCash Flow (last 4 years):")
print(cash_flow)