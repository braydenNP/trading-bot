import requests
import os
from auth import getAuth
from actions import TradingBot
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
bot = None
#setup code
def setupAuth():
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

def main():
    #setupAuth()
    bot = TradingBot(auth_token, account_id)

    while True:
        print("""
Choose an option
[1] Buy a stock and set a trailing stop loss immediately (only IDX)
[2] Set a trailing stop loss for an already bought stock (needs order id of stop loss)
[3] Check price of a stock
[4] Buy a stock at market price
[5] Sell a stock at market price
[6] Buy a stock at limit price
[7] Set a stoploss
[0] Exit
            """)
        selection = int(input("Select an option: "))
        match selection:
            case 0:
                print("0 selected, Exiting program")
                return
            case 1:
                symbol = input("Enter a symbol: ")
                usd_amount = int(input("Enter a sum of money(usd): "))
                order_id = buyAndMinimumStopLoss(usd_amount, symbol)
                print("order id of stop loss: ", order_id)
                time.sleep(1)
                trailingStopLoss(order_id)
            case 2:
                order_id = input("Enter an order id: ")
                trailingStopLoss(order_id)
            case 3:
                #check price of a stock
                symbol = input("Enter a symbol: ")
                print(f"Price of ${symbol}:")
                print(f"Buy: ${bot.buyPrice(symbol)}")
                print(f"Sell: ${bot.sellPrice(symbol)}")
            case 4:
                #BUY a stock (MARKET)
                symbol = input("Enter a symbol: ")
                print(f"current BUY price of ${symbol} is ${bot.buyPrice(symbol)}")
                print(f"current SELL price of ${symbol} is ${bot.sellPrice(symbol)}")

                quantity = int(input("Enter a quantity: "))
                confirm = input(f"Confirm to BUY ${quantity} of ${symbol}? (y/n): ")
                if confirm == 'y':
                    bot.buyOrderMarket(symbol, quantity)
                else:
                    print("Cancelled!")
            case 5:
                #SELL a stock (MARKET)
                symbol = input("Enter a symbol: ")
                print(f"current BUY price of ${symbol} is ${bot.buyPrice(symbol)}")
                print(f"current SELL price of ${symbol} is ${bot.sellPrice(symbol)}")

                quantity = int(input("Enter a quantity: "))
                confirm = input(f"Confirm to SELL ${quantity} of ${symbol}? (y/n): ")
                if confirm == 'y':
                    bot.sellOrderMarket(symbol, quantity)
                else:
                    print("Cancelled!")
            case 6:
                #BUY a stock (LIMIT)
                symbol = input("Enter a symbol: ")
                print(f"current BUY price of ${symbol} is ${bot.buyPrice(symbol)}")
                print(f"current SELL price of ${symbol} is ${bot.sellPrice(symbol)}")


                quantity = int(input("Enter a quantity: "))
                price = int(input("Enter a price: "))
                confirm = input(f"Confirm to BUY ${quantity} of ${symbol} at price:${price}? (y/n): ")
                if confirm == 'y':
                    bot.buyOrderLimit(symbol, quantity, price)
                else:
                    print("Cancelled!")
            case 7:
                #set STOPLOSS
                symbol = input("Enter a symbol: ")
                print(f"current BUY price of ${symbol} is ${bot.buyPrice(symbol)}")
                print(f"current SELL price of ${symbol} is ${bot.sellPrice(symbol)}")

                quantity = int(input("Enter a quantity: "))
                price = int(input("Enter a price: "))
                confirm = input(f"Confirm to set STOPLOSS for ${quantity} of ${symbol} at price:${price}? (y/n): ")
                if confirm == 'y':
                    bot.setStoploss(symbol, quantity, price)
                else:
                    print("Cancelled!")

if __name__ == "__main__":
    main()


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

