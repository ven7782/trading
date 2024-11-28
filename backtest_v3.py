import yfinance as yf
import pandas as pd
import sys
import quantstats as qs
qs.extend_pandas()

args = sys.argv

# from config_tickers import DOW_30_TICKER, NAS_100_TICKER, SP_500_TICKER, SINGLE_TICKER
DEREXION_BULL = ['MIDU', 'SPXL', 'TNA', 'EDC', 'EURL', 'KORU', 'MEXX', 'YINN', 'TYD', 'TMF', 'CURE', 'DFEN', 'DPST', 
                 'DRN', 'DUSL', 'FAS', 'HIBL', 'LABU', 'NAIL', 'PILL', 'RETL', 'SOXL', 'TECL', 'TPOR', 'UTSL', 'WANT', 
                 'WEBL', 'AIBU', 'BRZU', 'CHAU', 'CLDL', 'CWEB', 'ERX', 'EVAV', 'FNGG', 'GUSH', 'INDL', 'JNUG', 'LMBO', 
                 'NUGT', 'OOTO', 'QQQU', 'SPUU', 'UBOT', 'URAA', 'XXCH', 'AAPU', 'AMZU', 'AVL', 'GGLL', 'METU', 'MSFU', 
                 'MUU', 'NFXL', 'NVDU', 'TSLL', 'TSMX']

DEREXION_BEAR = ['SPXS', 'TZA', 'EDZ', 'YANG', 'TYO', 'TMV', 'DRV', 'FAZ', 'HIBS', 'LABD', 'SOXS', 'WEBS', 'AIBD',  # 'TECS', 
                 'ERY', 'DRIP', 'JDST', 'DUST', 'AAPD', 'AMZD', 'AVS', 'GGLS', 'METD', 'MSFD', 'MUD', 'NFXS', 'NVDD', 'TSLS', 
                 'TSMZ', 'QQQD', 'REKT', 'SPDN']

pd.set_option('display.max_rows', None)
pd.options.display.float_format = '{:.6f}'.format

def load_intraday_data(ticker, start_date, end_date):
    """Load intraday data from a CSV file for the given date range."""
    try:
        data = pd.read_csv(f"data/{ticker}.csv", parse_dates=["timestamp"])
        data = data[(data["timestamp"] >= start_date) & (data["timestamp"] <= end_date)]
        return data
    except FileNotFoundError:
        print(f"Intraday data file for {ticker} not found.")
        return pd.DataFrame()

def backtest_strategy(ticker, start_date, end_date, initial_capital):
    # Download historical data
    data = yf.download(ticker, start=start_date, end=end_date, multi_level_index=False).copy()
    data = data[['Open', 'High', 'Low', 'Close']]
    data.dropna(inplace=True)

    # Buy and Hold strategy for comparison
    buy_hold_shares = int(initial_capital / data.iloc[0]['Open'])
    residual = initial_capital - (buy_hold_shares * data.iloc[0]['Open'])

    # Add necessary columns
    data['Previous_Close'] = data['Close'].shift(1)
    # data['Buy_Signal'] = data['Open'] > data['Previous_Close']
    # data['Buy_Signal'] = (data['Open'] > data['Previous_Close']) & (data['Low'] < 0.99 * data['Open'])
    data['Buy_Signal'] = data['Low'] < 0.99 * data['Open']

    # Initialize variables
    capital = initial_capital
    position = 0
    trade_log = []
    result = []
    winning_trades = 0
    losing_trades = 0

    # Backtest loop
    for i, row in data.iterrows():
        # Buy and Hold balance each day
        buy_hold_balance = residual + (row['Close'] * buy_hold_shares)
        if position == 0:  # No open position
            if row['Buy_Signal']: # Buy signal
                buy_price = row['Open'] * 0.99
                intraday_data = load_intraday_data(ticker, f"{i} 09:30", f"{i} 16:30")
                if not intraday_data.empty:
                    for _, minute_row in intraday_data.iterrows():
                        if minute_row['Low'] < buy_price and position == 0:
                            buy_price = minute_row['Low']
                            position = int(capital / buy_price)  # Only buy whole shares
                            cost = position * buy_price
                            if position > 0:  # Proceed only if we can buy at least 1 share
                                capital -= cost  # Deduct cost from capital
                                balance = (position * buy_price) + capital
                                trade_log.append({
                                    'Date': minute_row['timestamp'],
                                    'Action': 'Buy',
                                    'Price': buy_price,
                                    'Capital': capital,
                                    'Position': position,
                                    'Balance': balance, 
                                    'Buy_Hold': buy_hold_balance
                                })
                        if minute_row['Open'] > buy_price * 1.01 and position > 0:
                            sell_price = minute_row['Open']
                            capital += position * sell_price
                            winning_trades += 1
                            balance = capital
                            trade_log.append({
                                'Date': minute_row['timestamp'], 
                                'Action': 'Sell (Target 1)', 
                                'Price': sell_price, 
                                'Capital': capital, 
                                'Position': 0,
                                'Balance': balance,
                                'Buy_Hold': buy_hold_balance
                            })
                            position = 0
                            break
                        if minute_row['Low'] < buy_price * 0.97 and position > 0:
                            sell_price = minute_row['Low']
                            capital += position * sell_price
                            losing_trades += 1
                            balance = capital
                            trade_log.append({
                                'Date': minute_row['timestamp'], 
                                'Action': 'Sell (Stop Loss 1)',
                                'Price': sell_price, 
                                'Capital': capital, 
                                'Position': 0,
                                'Balance': balance,
                                'Buy_Hold': buy_hold_balance
                            })
                            position = 0
                            break
        else:  # Open position exists
            # Load intraday data for the next day
            # next_day = i + datetime.timedelta(days=1)
            # intraday_data = load_intraday_data(ticker, f"{next_day} 09:31", f"{next_day} 16:30")
            intraday_data = load_intraday_data(ticker, f"{i} 09:30", f"{i} 16:30")

            if not intraday_data.empty:
                for _, minute_row in intraday_data.iterrows():
                    if minute_row['High'] >= buy_price * 1.02:  # Target hit
                        sell_price = minute_row['High']
                        capital += position * sell_price
                        winning_trades += 1
                        balance = capital
                        trade_log.append({
                            'Date': minute_row['timestamp'], 
                            'Action': 'Sell (Target 2)', 
                            'Price': sell_price, 
                            'Capital': capital, 
                            'Position': 0,
                            'Balance': balance,
                            'Buy_Hold': buy_hold_balance
                        })
                        position = 0
                        break
                    elif minute_row['Low'] <= buy_price * 0.99:  # Stop loss hit
                        sell_price = minute_row['Low']
                        capital += position * sell_price
                        losing_trades += 1
                        balance = capital
                        trade_log.append({
                            'Date': minute_row['timestamp'], 
                            'Action': 'Sell (Stop Loss 2)', 
                            'Price': sell_price, 
                            'Capital': capital, 
                            'Position': 0,
                            'Balance': balance,
                            'Buy_Hold': buy_hold_balance
                        })
                        position = 0
                        break
                if position > 0: # Neither target nor stop loss hit, sell at close
                    sell_price = row['Close']
                    capital += position * sell_price
                    losing_trades += 1 if sell_price < buy_price else 0
                    winning_trades += 1 if sell_price > buy_price else 0
                    balance = capital
                    trade_log.append({
                        'Date': i,
                        'Action': 'Sell (Close)',
                        'Price': sell_price,
                        'Capital': capital,
                        'Position': 0,
                        'Balance': balance,
                        'Buy_Hold': buy_hold_balance
                    })
                    position = 0  # Reset position

    # Compile trade log into DataFrame
    trade_df = pd.DataFrame(trade_log)

    # Calculate the Maximum Drawdown for 'Balance'
    # Maximum drawdown is the maximum loss from a peak to a trough in the balance
    trade_df['Peak'] = trade_df['Balance'].cummax()  # Get the running peak
    trade_df['Drawdown'] = trade_df['Balance'] / trade_df['Peak'] - 1  # Calculate the drawdown
    max_drawdown = trade_df['Drawdown'].min()  # Find the maximum drawdown
    trade_df = trade_df.drop(columns=['Peak', 'Drawdown'])

    # Final results
    final_balance = capital if position == 0 else (position * data.iloc[-1]['Close']) + capital
    net_profit = final_balance - initial_capital
    percentage_gain = (net_profit / initial_capital) * 100
    total_trades = winning_trades + losing_trades
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0

    # Display results
    print(f"Final Balance: ${final_balance:.2f}")
    print(f"Net Profit: ${net_profit:.2f}")
    print(f"Percentage Gain: {percentage_gain:.2f}%")
    print(f"Winning Trades: {winning_trades}")
    print(f"Losing Trades: {losing_trades}")
    print(f"Win Rate: {win_rate:.2f}%")
    print(f"Maximum Drawdown: {max_drawdown * 100:.2f}%")

    result = ({
        'Ticker': ticker,
        'Final Balance': final_balance,
        'Buy Hold': buy_hold_balance,
        'Net Profit': net_profit,
        'Percentage Gain': percentage_gain,
        'Win Rate': win_rate,
        'Maximum Drawdown': max_drawdown
    })

    return trade_df, result

# Parameters
# Get the command line arguments
# args = sys.argv
# tickers = ['NVDA']
# ticker = args[1]
initial_capital = 10000

start_date = "2024-11-01"
end_date = "2024-11-28"

data = []

tickers = [args[1]]
# Run the backtest
for ticker in tickers:
    print(30*"=")
    print(f"Results for: {ticker}")
    trade_results, stats = backtest_strategy(ticker, start_date, end_date, initial_capital)
    data.append(stats)
    print(30*"=")

stats_df = pd.DataFrame(data)
stats_df = stats_df.sort_values(by='Percentage Gain', ascending=False)
# stats_df.to_csv(f'bear.csv')
print(stats_df)
print(trade_results)