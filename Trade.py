import requests, json, collections
import pandas as pd
import time
from config import *
from screen import *

yahoo_url = "https://uk.finance.yahoo.com/screener/predefined/day_gainers"
td_url = r"https://api.tdameritrade.com/v1/marketdata/quotes"
historic_data_url = "https://api.tdameritrade.com/v1/marketdata/"
alpaca_base_url = "https://paper-api.alpaca.markets"
order_url = f"{alpaca_base_url}/v2/orders"
account_url = f"{alpaca_base_url}/v2/account"
clock_url = f"{alpaca_base_url}/v2/clock"
positions_url = f"{alpaca_base_url}/v2/positions"
headers = {"APCA-API-KEY-ID": alpaca_key, "APCA-API-SECRET-KEY": secret_key}


def order_variables():
    buying_power = account_info["buying_power"]
    order_data = use_tickers[["symbol", "askPrice"]]
    available_to_spend = float(buying_power) * 0.85
    power_per_share = float(available_to_spend) / len(order_data)  
    order_data["qty"] = power_per_share / use_tickers["askPrice"].values
    order_data["qty"] = [int(qty) for qty in order_data["qty"].values]
    order_data["side"] = "buy"
    order_data["type"] = "market"
    order_data["TIF"] = "day"
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


def close_position(symbol):
    close_order = requests.delete(f"{positions_url}/{symbol}", headers=headers)
    return json.loads(close_order.content)


while get_clock["is_open"] == True:
    profit_loss_list = {}
    sorted_pl_list = sorted(profit_loss_list.items(), key=lambda kv: kv[1])
    profit_loss_list = collections.OrderedDict(sorted_pl_list)

    for position in open_positions:
        symbol = position["symbol"]
        buy_price = position["avg_entry_price"]
        profit_loss = position["unrealized_pl"]
        stop_loss = float(buy_price) * 0.975
        profit =  float(profit_loss) / float(buy_price) * 100
        profit_loss_list.update({symbol: profit})
        position_size = int(position["qty"])
        take_profit = float(buy_price) * 1.2

        if float(position["current_price"]) <= stop_loss:
            print(close_position(symbol))
            print(f"position in {symbol} liqudated")
        
        elif float(position["current_price"]) >= take_profit:
            print(close_position(symbol))
            print(f"position in {symbol} liquated")

        else:
            pass

    time.sleep(5)


# avoid pattern day trading rule - need to change strategy to hold trades for 2-5 days 
# - if stock has been bought within the last 5 days remove it from screened stocks before running through the ml algorithm

# integrate ml algo to screening strategy
# - get historic data from TD API that matches data used to train the MSFT model 
# - preprocess the data from TD 
# - import the pickled classifier and run it on the data ** AFTER OTHER SCREENING STRATEGIES ARE COMPLETE **
