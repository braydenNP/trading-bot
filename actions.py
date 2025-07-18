order_url = "https://ic.cgsi.com/api/v1/order"
fee_url = "https://ic.cgsi.com/api/v1/fee"
headers = {
    "Host": "ic.cgsi.com",
    #"Authorization": auth_token,
    "Cache-Control": "no-cache",
    "Accept-Language": "en-US,en;q=0.9",
    "Sec-Ch-Ua": '"Chromium";v="131", "Not_A Brand";v="24"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.140 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json",
    "Environment": "cic",
    "Origin": "https://ic.cgsi.com",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Referer": "https://ic.cgsi.com/",
    "Accept-Encoding": "gzip, deflate, br",
    "Priority": "u=1, i"
}
import requests

class TradingBot:
    def __init__(self, auth_token, account_id):
        self.auth_token = auth_token
        self.account_id = account_id
        self.session = requests.Session()
        self.headers = headers
        headers["Authorization"] = auth_token


    def buyPrice(self, symbol):
        payload = {
            "account_id": self.account_id,
            "symbol": symbol,
            "duration": "DAY",
            "side": "BUY",
            "order_type": "MARKET",
            "quantity": 1
        }
        response = self.session.post(fee_url, headers=self.headers, json=payload)
        if response.status_code == 200:
            return(response.json()["data"]["price"])
        else:
            raise Exception("Check Buy Price api error")

    def sellPrice(self, symbol):
        payload = {
            "account_id": self.account_id,
            "symbol": symbol,
            "duration": "DAY",
            "side": "SELL",
            "order_type": "MARKET",
            "quantity": 1
        }
        response = self.session.post(fee_url, headers=self.headers, json=payload)
        if response.status_code == 200:
            return(response.json()["data"]["price"])
        else:
            raise Exception("Check Sell Price api error")


    def buyOrderLimit(self, symbol, quantity, price):
        payload = {
            "account_id": self.account_id,
            "symbol": symbol,
            "duration": "DAY",
            "side": "BUY",
            "order_type": "LIMIT",
            "quantity": quantity,
            "limit_price": price
        }
        response = self.session.post(order_url, headers=self.headers, json=payload)
        if response.status_code != 200:
            raise Exception("Buy Order Limit error")

    # def sellOrderLimit(self, symbol, quantity, price):
    #     payload = {
    #         "account_id": self.account_id,
    #         "symbol": symbol,
    #         "duration": "DAY",
    #         "side": "SELL",
    #         "order_type": "LIMIT",
    #         "quantity": quantity,
    #         "limit_price": price
    #     }
    #     response = self.session.post(order_url, headers=self.headers, json=payload)
    #     if response.status_code != 200:
    #         raise Exception("Buy Order Limit error")
        
    def buyOrderMarket(self, symbol, quantity):
        payload = {
            "account_id": self.account_id,
            "symbol": symbol,
            "duration": "DAY",
            "side": "BUY",
            "order_type": "MARKET",
            "quantity": quantity
        }
        response = self.session.post(order_url, headers=self.headers, json=payload)
        if response.status_code != 200:
            raise Exception("Buy Order Market error")
        
    def sellOrderMarket(self, symbol, quantity):
        payload = {
            "account_id": self.account_id,
            "symbol": symbol,
            "duration": "DAY",
            "side": "SELL",
            "order_type": "MARKET",
            "quantity": quantity
        }
        response = self.session.post(order_url, headers=self.headers, json=payload)
        if response.status_code != 200:
            raise Exception("Sell Order Market error")
        
    #returns the order_id
    def setStoploss(self, symbol, quantity, price):
        payload = {
            "account_id": self.account_id,
            "symbol": symbol,
            "duration": "GTC",
            "side": "SELL",
            "order_type": "STOPLOSS",
            "quantity": quantity,
            "trigger_by": "PRICE",
            "trigger_price": price
        }
        response = self.session.post(order_url, headers=self.headers, json=payload)
        if response.status_code != 200:
            raise Exception("Sell Stoploss error")
        else:
            return(response.json()["data"]["order_id"])
        
    def getStoploss(self, order_id):
        response = self.session.get(f"{order_url}/{order_id}", headers=self.headers)
        if response.status_code != 200:
            print(f"API request failed with status {response.status_code}")
            print(f"Response text: {response.text}")
            return None
    
        # Check if response has content
        if not response.text.strip():
            print("Empty response from API")
            return None
        
        try:
            data = response.json()
            
            # Check if data key exists and has items
            if "data" in data and data["data"] and data["data"][0]:
                return data["data"][0]
            else:
                print("No data in response or empty data array")
                return None
                
        except Exception as e:
            print(f"Error parsing JSON: {e}")
            print(f"Response text: {response.text}")
            print(f"Response headers: {response.headers}")
            return None


    def cancelStoploss(self, order_id):
        response = self.session.delete(f"{order_url}/{order_id}", headers=self.headers)
        if response.status_code != 200:
            raise Exception("Sell Stoploss error")
        
    def modifyStoploss(self, order_id, quantity, price):
        payload = {
            "quantity": quantity,
            "trigger_price": price
        }
        response = self.session.put(f"{order_url}/{order_id}", headers=self.headers, json=payload)
        if response.status_code != 200:
            raise Exception("Edit Stoploss error")