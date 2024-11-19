import yfinance as yf
import pandas as pd
import sys
from config_tickers import DOW_30_TICKER, NAS_100_TICKER, SP_500_TICKER, SINGLE_TICKER
DEREXION_BULL = ['MIDU', 'SPXL', 'TNA', 'EDC', 'EURL', 'KORU', 'MEXX', 'YINN', 'TYD', 'TMF', 'CURE', 'DFEN', 'DPST', 
                 'DRN', 'DUSL', 'FAS', 'HIBL', 'LABU', 'NAIL', 'PILL', 'RETL', 'SOXL', 'TECL', 'TPOR', 'UTSL', 'WANT', 
                 'WEBL', 'AIBU', 'BRZU', 'CHAU', 'CLDL', 'CWEB', 'ERX', 'EVAV', 'FNGG', 'GUSH', 'INDL', 'JNUG', 'LMBO', 
                 'NUGT', 'OOTO', 'QQQU', 'SPUU', 'UBOT', 'URAA', 'XXCH', 'AAPU', 'AMZU', 'AVL', 'GGLL', 'METU', 'MSFU', 
                 'MUU', 'NFXL', 'NVDU', 'TSLL', 'TSMX']

DEREXION_BEAR = ['SPXS', 'TZA', 'EDZ', 'YANG', 'TYO', 'TMV', 'DRV', 'FAZ', 'HIBS', 'LABD', 'SOXS', 'TECS', 'WEBS', 'AIBD', 
                 'ERY', 'DRIP', 'JDST', 'DUST', 'AAPD', 'AMZD', 'AVS', 'GGLS', 'METD', 'MSFD', 'MUD', 'NFXS', 'NVDD', 'TSLS', 
                 'TSMZ', 'QQQD', 'REKT', 'SPDN']

pd.set_option('display.max_rows', None)
pd.options.display.float_format = '{:.6f}'.format

def backtest_strategy(ticker, start_date, end_date, initial_capital):
    # Download historical data
    data = yf.download(ticker, start=start_date, end=end_date).copy()
    data = data[['Open', 'High', 'Low', 'Close']]
    data.dropna(inplace=True)

    # Buy and Hold strategy for comparison
    buy_hold_shares = int(initial_capital / data.iloc[0]['Open'])
    residual = initial_capital - (buy_hold_shares * data.iloc[0]['Open'])

    # Add necessary columns
    data['Previous_Close'] = data['Close'].shift(1)
    data['Buy_Signal'] = data['Open'] > data['Previous_Close']
    # data['Buy_Signal'] = True
    data['Sell_Target'] = data['Open'] * 1.02  # 2% above open
    data['Stop_Loss'] = data['Open'] * 0.99   # 1% below open

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
            if row['Buy_Signal']:  # Buy signal
                buy_price = row['Open']
                position = int(capital / buy_price)  # Only buy whole shares
                cost = position * buy_price
                if position > 0:  # Proceed only if we can buy at least 1 share
                    capital -= cost  # Deduct cost from capital
                    balance = (position * buy_price) + capital
                    trade_log.append({
                        'Date': i,
                        'Action': 'Buy',
                        'Price': buy_price,
                        'Capital': capital,
                        'Position': position,
                        'Balance': balance, 
                        'Buy_Hold': buy_hold_balance
                    })
        else:  # Open position exists
            if row['High'] >= row['Sell_Target']:  # Target hit
                sell_price = row['Sell_Target']
                capital += position * sell_price
                winning_trades += 1
                balance = capital
                trade_log.append({
                    'Date': i,
                    'Action': 'Sell (Target)',
                    'Price': sell_price,
                    'Capital': capital,
                    'Position': 0,
                    'Balance': balance,
                    'Buy_Hold': buy_hold_balance
                })
                position = 0  # Reset position
            elif row['Low'] <= row['Stop_Loss']:  # Stop loss hit
                sell_price = row['Stop_Loss']
                capital += position * sell_price
                losing_trades += 1 if sell_price < buy_price else 0
                winning_trades += 1 if sell_price > buy_price else 0
                balance = capital
                trade_log.append({
                    'Date': i,
                    'Action': 'Sell (Stop Loss)',
                    'Price': sell_price,
                    'Capital': capital,
                    'Position': 0,
                    'Balance': balance,
                    'Buy_Hold': buy_hold_balance
                })
                position = 0  # Reset position
            else:  # Neither target nor stop loss hit, sell at close
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

    # Final results
    final_balance = capital if position == 0 else (position * data.iloc[-1]['Close']) + capital
    net_profit = final_balance - initial_capital
    percentage_gain = (net_profit / initial_capital) * 100
    total_trades = winning_trades + losing_trades
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0

    # Display results
    print(f"Final Balance: ${final_balance:.2f}")
    print(f"Buy and Hold Balance: ${buy_hold_balance:.2f}")
    print(f"Net Profit: ${net_profit:.2f}")
    print(f"Percentage Gain: {percentage_gain:.2f}%")
    print(f"Winning Trades: {winning_trades}")
    print(f"Losing Trades: {losing_trades}")
    print(f"Win Rate: {win_rate:.2f}%")

    result = ({
        'Ticker': ticker,
        'Final Balance': final_balance,
        'Buy Hold': buy_hold_balance,
        'Net Profit': net_profit,
        'Percentage Gain': percentage_gain,
        'Win Rate': win_rate
    })

    return trade_df, result

# Parameters
# Get the command line arguments
args = sys.argv
# tickers = ['NVDA']
# ticker = args[1]
initial_capital = 100000

start_date = "2024-01-01"
end_date = "2024-11-18"

data = []

# Run the backtest
for ticker in SINGLE_TICKER:
    print(30*"=")
    print(f"Results for: {ticker}")
    trade_results, stats = backtest_strategy(ticker, start_date, end_date, initial_capital)
    data.append(stats)
    print(30*"=")

stats_df = pd.DataFrame(data)
stats_df = stats_df.sort_values(by='Percentage Gain', ascending=False)
# stats_df.to_csv(f'bear.csv')
print(stats_df)
# print(trade_results)