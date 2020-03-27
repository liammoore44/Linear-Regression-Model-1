import requests, json, collections
import pandas as pd
import time
from config import alpaca_key, secret_key, td_key
from machine_learning_screener import *

td_quotes_url = r"https://api.tdameritrade.com/v1/marketdata/quotes"
alpaca_base_url = "https://paper-api.alpaca.markets"
order_url = f"{alpaca_base_url}/v2/orders"
account_url = f"{alpaca_base_url}/v2/account"
clock_url = f"{alpaca_base_url}/v2/clock"
positions_url = f"{alpaca_base_url}/v2/positions"
headers = {"APCA-API-KEY-ID": alpaca_key, "APCA-API-SECRET-KEY": secret_key}


def get_account():
    account = requests.get(account_url, headers=headers)
    return json.loads(account.content)

account_info = get_account()


def get_clock():
    request = requests.get(clock_url, headers=headers)
    return json.loads(request.content)


def get_stock_data():
    parameters = {
    "apikey": td_key,
    "symbol": tickers
    }
    request = requests.get(url=td_quotes_url, params=parameters).json()
    data = pd.DataFrame.from_dict(request, orient='index').reset_index(drop=True)
    return data
use_tickers = get_stock_data()


def order_variables():
    buying_power = account_info["buying_power"]
    order_data = use_tickers[["symbol", "askPrice"]]
    available_to_spend = float(buying_power) 
    power_per_share = float(available_to_spend) / len(order_data)  
    order_data["qty"] = power_per_share / use_tickers["askPrice"].values
    order_data["qty"] = [int(qty) for qty in order_data["qty"].values]
    order_data["type"] = "market"
    order_data["TIF"] = "day"
    for symbol in order_data['symbol']:
        # if symbol in sell_tickers:
        #     order_data["side"] = 'sell'
        if symbol in buy_tickers:
            order_data['side'] = 'buy'
    order_data = order_data[["symbol", "qty", "side", "type", "TIF"]]
    return order_data

order_variables = order_variables()


def order(symbol, qty, side, type, time_in_force):
    parameters = {
    "symbol": symbol,
    "qty": qty,
    "side": side,
    "type": type,
    "time_in_force": time_in_force,
    }
    request = requests.post(order_url, json=parameters, headers=headers)
    return json.loads(request.content)

for row in order_variables.values:
    order(row[0], row[1], row[2], row[3], row[4])
    print(f"{row[2]} order of {row[1]} shares in {row[0]} complete.")


def open_positions():
    request = requests.get(positions_url, headers=headers)
    return json.loads(request.content)

open_positions = open_positions()


def take_profit_loss():
    for position in open_positions:
        symbol = position['symbol']
        loss_amount = {
        0.96: int(position['qty']),
        0.97: int(position['qty'])*0.6, 
        }
        profit_amount = { 
        1.055: int(position['qty'])*0.2, 
        1.7: int(position['qty'])*0.3, 
        1.85: int(position['qty'])*0.25, 
        1.1: int(position['qty'])* 0.35,
        1.12: int(position['qty'])
        }

        for key, value in list(profit_amount.items()):

            if float(position['current_price']) >= float(key)* float(position['avg_entry_price']):
                order(position['symbol'], int(value), 'sell', 'market', 'gtc')
                profit_amount.pop(key)
                print(f"Sold {value} shares in {symbol}")
            else:
                print('-')
                
        for key, value in list(loss_amount.items()):
            if float(position['current_price']) <= float(key)* float(position['avg_entry_price']):
                order(position['symbol'], int(value), 'sell', 'market', 'gtc')
                loss_amount.pop(key)
                print(f"Sold {value} shares in {symbol}")    
            
            else:
                print('-')
    
    return order


# def take_loss():
#     for position in open_positions:
#         symbol = position['symbol']

#         sell_amount = {0.98: int(position['qty'])*0.7, 0.97: int(position['qty'])}

#         for key, value in list(sell_amount.items()):
#             if float(position['current_price']) <= float(key)* float(position['avg_entry_price']):
#                 order(position['symbol'], float(value), 'sell', 'market', 'gtc')
#                 sell_amount.pop(key)
#                 print(f"Sold {value} shares in {symbol}")
#     return order

 
while get_clock()["is_open"] == True:
    
    take_profit_loss()
    time.sleep(5)
