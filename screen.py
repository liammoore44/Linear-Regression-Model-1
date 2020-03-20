import requests, json, collections
import pandas as pd
import time
from config import *

yahoo_url = "https://uk.finance.yahoo.com/screener/predefined/day_gainers"
td_url = r"https://api.tdameritrade.com/v1/marketdata/quotes"
historic_data_url = "https://api.tdameritrade.com/v1/marketdata/"
alpaca_base_url = "https://paper-api.alpaca.markets"
order_url = f"{alpaca_base_url}/v2/orders"
account_url = f"{alpaca_base_url}/v2/account"
clock_url = f"{alpaca_base_url}/v2/clock"
positions_url = f"{alpaca_base_url}/v2/positions"
headers = {"APCA-API-KEY-ID": alpaca_key, "APCA-API-SECRET-KEY": secret_key}

df = pd.read_html(yahoo_url)[0]
tickers = [symbol for symbol in df["Symbol"]]


def get_stock_data():
    parameters = {
    "apikey": td_key,
    "symbol": tickers
    }
    request = requests.get(url=td_url, params=parameters).json()
    data = pd.DataFrame.from_dict(request, orient='index').reset_index(drop=True)
    return data

stock_data = get_stock_data()

def get_account():
    account = requests.get(account_url, headers=headers)
    return json.loads(account.content)

account_info = get_account()


def get_clock():
    request = requests.get(clock_url, headers=headers)
    return json.loads(request.content)

get_clock = get_clock()


def screening_strategy():
    tickers = stock_data.loc[(stock_data["lastPrice"] > 6)]
    tickers = tickers.loc[(stock_data["lastPrice"] < 70)]
    tickers = tickers.loc[(stock_data["totalVolume"] > 100000)]
    tickers = tickers.loc[(stock_data["lastPrice"] - stock_data["lowPrice"]) > (stock_data["highPrice"] - stock_data["lastPrice"])]
    return tickers

use_tickers = screening_strategy()
ticker_list = [ticker for ticker in use_tickers['symbol']]
print(ticker_list)

def get_historic_data():
    parameters = {
    "apikey": td_key,
    "period": 10,
    "periodType": "year"
    }
    list_of_dataframes = []
    for ticker in ticker_list:
        request = requests.get(url=f"{historic_data_url}/{ticker}/pricehistory", params=parameters).json()
        historic_data = pd.DataFrame(request).reset_index(drop=True)
        df = pd.DataFrame(list(historic_data['candles']))
        list_of_dataframes.append(df) 
    return(list_of_dataframes)

historic_data = get_historic_data()
print(historic_data)