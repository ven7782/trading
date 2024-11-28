import requests
import pandas as pd
from datetime import datetime, timedelta
import sys

args = sys.argv

def fetch_paginated_minute_data(api_key, ticker, start_date, end_date):
    """
    Fetches minute-level data with pagination from Polygon.io.

    Args:
        api_key (str): Your Polygon.io API key.
        ticker (str): Stock ticker symbol.
        start_date (str): Start date in 'YYYY-MM-DD' format.
        end_date (str): End date in 'YYYY-MM-DD' format.

    Returns:
        pd.DataFrame: A DataFrame with all minute-level data.
    """
    base_url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/minute"
    all_data = []
    current_start_date = start_date

    while True:
        print(f"Fetching data from {current_start_date} to {end_date}...")
        params = {
            "adjusted": "true",
            "sort": "asc",
            "limit": 50000,
            "apiKey": api_key
        }
        url = f"{base_url}/{current_start_date}/{end_date}"
        response = requests.get(url, params=params)

        if response.status_code == 200:
            data = response.json()
            if "results" in data:
                all_data.extend(data["results"])

                if len(data["results"]) < 50000:
                    break

                # Update current_start_date for next batch (strip time for compliance)
                last_timestamp = data["results"][-1]["t"]
                current_start_date = datetime.utcfromtimestamp(last_timestamp / 1000).strftime("%Y-%m-%d")
            else:
                print("No more data available.")
                break
        else:
            print(f"Error: {response.status_code}, {response.text}")
            break

    if all_data:
        df = pd.DataFrame(all_data)
        df['timestamp'] = pd.to_datetime(df['t'], unit='ms')
        df = df.rename(columns={
            'o': 'Open', 'h': 'High', 'l': 'Low', 'c': 'Close', 'v': 'Volume'
        })
        df = df[['timestamp', 'Open', 'High', 'Low', 'Close', 'Volume']]
        return df
    else:
        print("No data fetched.")
        return pd.DataFrame()

# Example usage
api_key = "9DtepbbaBrTstAj9Rm4WQracoXiH9BkV"  # Replace with your Polygon.io API key
# ticker = "ERY"
ticker = args[1]
start_date = "2024-01-01"
end_date = "2024-11-27"

minute_data = fetch_paginated_minute_data(api_key, ticker, start_date, end_date)
minute_data.to_csv(f'data/{ticker}.csv')

if not minute_data.empty:
    print(f"Fetched {len(minute_data)} records.")
    print(minute_data.head())
else:
    print("No data retrieved.")
