import requests
import os
from auth import getAuth
from actions import TradingBot
from urllib.parse import urljoin
from datetime import datetime
import time
from dotenv import load_dotenv
load_dotenv()


#conda activate myenv
session = requests.Session()
account_id = os.getenv('ACCOUNT_ID')
username = os.getenv('USER_NAME')
password = os.getenv('PASSWORD')
pin = os.getenv('PIN')
auth_token = ''
price=''
total_bal = 60000
#setup code
if os.path.exists("auth.txt"):
    with open("auth.txt", "r") as file:
        auth_token = file.read()
        try: 
            bot = TradingBot(auth_token, account_id)
            price = bot.buyPrice("PACK.XIDX")
        except Exception as e:
            print("GETTING PRICE FAILED")
            auth_token = getAuth(username, password, pin)
            with open("auth.txt", "w") as file:
                file.write(auth_token)
else:
    print("auth.txt not found.")
    auth_token = getAuth(username, password, pin)
    with open("auth.txt", "w") as file:
        file.write(auth_token)

bot = TradingBot(auth_token, account_id)
def buyAndMinimumStopLoss(usd_amount, symbol):
    fx_rate = 1
    if 'XIDX' in symbol:
        fx_rate = 16025
        money = usd_amount*fx_rate
        buyPrice = bot.buyPrice(symbol)
        sellPrice = bot.sellPrice(symbol)
        quantity = int(round(int(money) / int(buyPrice), -2))

        print("Buy price is:", buyPrice, "\nSell price is", sellPrice, "\nQuantity of stock is", quantity)
        approve = input("yes to approve: ")
        if approve == "yes":
            bot.buyOrderMarket(symbol, quantity)
            for price in range(int(sellPrice), 0, -10):
                try:
                    order_id = bot.setStoploss(symbol, quantity, price)
                    print("stop loss for", symbol, "set at", price)
                    return order_id
                except Exception as e:
                    continue
def trailingStopLoss(order_id):
    failed = 0
    max_failures = 50
    timeout_duration = 15
    check_interval = 2
    
    print(f"Starting trailing stop loss for order {order_id}")
    
    while True:
        try:
            # Get current stoploss data
            data = bot.getStoploss(order_id)
            
            # Check if data retrieval failed
            if data is None:
                print("Failed to get stoploss data, retrying...")
                time.sleep(2)
                continue
            
            # Check if order is filled
            filled = data.get("filled", 0)
            if filled != 0:
                print(f"Order filled: {filled} shares. Stopping trailing stop loss.")
                return
            
            # Get current values
            trigger_price = data.get("trigger_price")
            quantity = data.get("quantity")
            
            if trigger_price is None or quantity is None:
                print("Missing required data from API response")
                time.sleep(2)
                continue
            
            # Calculate new trigger price
            new_trigger = trigger_price + 10
            
            # Try to modify stoploss
            if failed < max_failures:
                try:
                    bot.modifyStoploss(order_id, quantity, new_trigger)
                    print(f"Stop loss increased from {trigger_price} to {new_trigger}")
                    failed = 0  # Reset failed counter on success
                    
                    # Wait before next check
                    time.sleep(check_interval)
                    
                except Exception as e:
                    failed += 1
                    print(f"Failed to modify stoploss (attempt {failed}/{max_failures}): {e}")
                    
                    # Short delay before retrying
                    time.sleep(1)
            else:
                print(f"Max failures ({max_failures}) reached, timeout {timeout_duration} seconds")
                time.sleep(timeout_duration)
                failed = 0  # Reset counter after timeout
                
        except KeyboardInterrupt:
            print("Trailing stop loss interrupted by user")
            break
        except Exception as e:
            print(f"Unexpected error in trailing stop loss: {e}")
            time.sleep(2)

#main code
symbol = input("Enter a symbol: ")
usd_amount = int(input("Enter a sum of money(usd): "))
order_id = buyAndMinimumStopLoss(usd_amount, symbol)
time.sleep(1)
trailingStopLoss(order_id)