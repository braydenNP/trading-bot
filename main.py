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
username = os.getenv('USERNAME')
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
    while True:
        data = bot.getStoploss(order_id)
        trigger_price = data["trigger_price"]
        new_trigger = trigger_price + 10
        failed = 0
        quantity = data["quantity"]
        filled = data["filled"]
        if filled != 0:
            return
        if failed < 50:
            try: 
                bot.modifyStoploss(order_id, quantity, new_trigger)
                new_trigger += 10
                print("stop loss increased to", new_trigger)
                failed = 0
            except Exception as e:
                failed += 1
        else:
            print("time out 15 seconds")
            time.sleep(15)
            failed = 49

#main code
symbol = input("Enter a symbol: ")
usd_amount = int(input("Enter a sum of money(usd): "))
order_id = buyAndMinimumStopLoss(usd_amount, symbol)
time.sleep(1)
trailingStopLoss(order_id)