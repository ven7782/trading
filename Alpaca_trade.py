import alpaca_trade_api as tradeapi
from datetime import datetime, timedelta
import time

# Alpaca API credentials
API_KEY = ''
API_SECRET = ''
BASE_URL = 'https://paper-api.alpaca.markets/'

# Initialize Alpaca API
api = tradeapi.REST(API_KEY, API_SECRET, BASE_URL, api_version='v2')

# Strategy parameters
SYMBOL = 'SOXL'
CAPITAL_PER_TRADE = 50000  # Capital allocated per trade

def place_day_sell_order(symbol, quantity, sell_price):
    # Place a day sell order
    order = api.submit_order(
        symbol=symbol,
        qty=quantity,
        side='sell',
        type='limit',
        time_in_force='day',
        limit_price=sell_price
    )
    print(f"Day sell order placed: {order}")

def place_bracket_order(symbol, quantity, take_profit_price, stop_loss_price):
    """
    Places a bracket order with take-profit and stop-loss conditions.
    
    :param symbol: The stock/ETF symbol (e.g., "SOXL")
    :param quantity: Number of shares to trade
    :param buy_price: Price at which shares were purchased
    :param take_profit_price: Price to sell for a profit
    :param stop_loss_price: Price to sell to minimize loss
    :return: The submitted bracket order
    """
    try:
        order = api.submit_order(
            symbol=symbol,
            qty=quantity,
            side='sell',
            type='limit',
            time_in_force='gtc',
            order_class='bracket',
            limit_price=take_profit_price,  # Take-profit price
            stop_loss={
                "stop_price": stop_loss_price  # Stop-loss trigger price
            }
        )
        print(f"Bracket order placed: {order}")
        return order
    except Exception as e:
        print(f"Failed to place bracket order: {e}")
        return None

def handle_market_close(symbol):
    """
    Cancel any active orders and sell all shares at market just before the market closes.
    
    :param symbol: The stock/ETF symbol (e.g., "SOXL")
    """
    # Monitor the time to close
    clock = api.get_clock()
    time_until_close = (clock.next_close - clock.timestamp).total_seconds()

    # Wait until close is near (around 4:29 PM ET)
    while time_until_close > 60:  # 1 minute before close
        print(f"Time until market close: {time_until_close // 60} minutes.")
        time.sleep(30)  # Check every 30 seconds
        clock = api.get_clock()
        time_until_close = (clock.next_close - clock.timestamp).total_seconds()

    print("Market close is near. Canceling any active orders...")
    
    # Cancel all active orders
    active_orders = api.list_orders(status='open', symbols=[symbol])
    for order in active_orders:
        api.cancel_order(order.id)
        print(f"Canceled order: {order.id}")

    # Sell all shares at market
    try:
        position = api.get_position(symbol)
        quantity = int(position.qty)
        print(f"Selling {quantity} shares at market before close.")
        api.submit_order(
            symbol=symbol,
            qty=quantity,
            side='sell',
            type='market',
            time_in_force='day'
        )
    except Exception as e:
        print(f"No position to sell at market close. Error: {e}")

    print("All actions completed for the day.")        

def main():
    while True:
        # Get the current time
        current_time = datetime.now()

        # Calculate the target time (next day's date at 9:30 AM)
        if datetime.now().strftime("%H:%M:%S") < "16:00:00":
            target_time = current_time.replace(hour=9, minute=30, second=0, microsecond=0)
        else:
            next_day = current_time + timedelta(days=1)
            target_time = next_day.replace(hour=9, minute=30, second=0, microsecond=0)

        # Wait until the target time
        while True:
            current_time = datetime.now()
            print(f"Current time: {current_time.strftime('%H:%M:%S')}", end="\r")
            if current_time >= target_time:
                break
            time.sleep(1)

        # Get current date and market status
        clock = api.get_clock()
        if not clock.is_open:
            print("Market is closed. Waiting for market to open...")
            time.sleep(10)  # Wait a minute before checking again
            continue

        # Determine next action based on the previous day's position
        try:
            # Check if there's an existing position
            position = api.get_position(SYMBOL)
            buy_price = float(position.avg_entry_price)
            quantity = int(position.qty)

            print(f"Existing position detected: {quantity} shares at ${buy_price:.2f}")
            
            # Place a bracket order for take-profit and stop-loss
            take_profit_price = round(buy_price * 1.02, 2)
            stop_loss_price = round(buy_price * 0.99, 2)
            bracket_order = place_bracket_order(SYMBOL, quantity, take_profit_price, stop_loss_price)

            print(f"Bracket order placed: {bracket_order}")

            # Check if the bracket order is still active
            # if yes, monitor and take appropriate actions
            handle_market_close(SYMBOL)

        except Exception as e:
            print(f"No existing position detected. Starting new strategy. Error: {e}")

            # Get today's open price
            bars = api.get_barset(SYMBOL, '1D', limit=2)[SYMBOL]
            if len(bars) < 2:
                print("Not enough data to proceed.")
                time.sleep(10)
                continue

            today_open = bars[-1].o
            limit_buy_price = round(today_open * 0.99, 2)

            # Place a limit buy order
            buy_order = api.submit_order(
                symbol=SYMBOL,
                qty=int(CAPITAL_PER_TRADE / limit_buy_price),
                side='buy',
                type='limit',
                time_in_force='day',
                limit_price=limit_buy_price
            )
            print(f"Limit buy order placed: {buy_order}")

            # Wait for the buy order to execute
            print("Waiting for limit buy order to fill...")
            while True:
                order_status = api.get_order(buy_order.id)
                if order_status.status == 'filled':
                    print(f"Buy order executed: {order_status}")
                    break
                elif order_status.status in ['canceled', 'expired']:
                    print(f"Buy order was {order_status.status}. Exiting strategy for today.")
                    break
                time.sleep(60)  # Check order status every minute

            if order_status.status == 'filled':
                time.sleep(10) # Wait for few secs before placing a sell order to avoid alpaca error
                # Get the quantity filled
                quantity = int(order_status.filled_qty)

                # Calculate sell price for 1% profit or stop limit at 3% loss
                day_sell_price = round(limit_buy_price * 1.01, 2)
                day_stop_limit_price = round(limit_buy_price * 0.97, 2)

                bracket_order = place_bracket_order(SYMBOL, quantity, day_sell_price, day_stop_limit_price)

                print(f"Bracket order placed: {bracket_order}")

                # Check if the bracket order is still active
                # if yes, monitor and take appropriate actions
                handle_market_close(SYMBOL)

        print("Strategy complete for the day. Waiting for the next trading day...")
        # time.sleep(60 * 60 * 12)  # Sleep for 12 hours before checking next trading day

if __name__ == "__main__":
    main()
