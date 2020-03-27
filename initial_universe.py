import requests, json, collections
import pandas as pd
import time
from datetime import datetime, date
import cProfile, pstats, io
import csv  

from config import td_key, alphavantage_key
from alpha_vantage.timeseries import TimeSeries


yahoo_url = "https://uk.finance.yahoo.com/screener/predefined/"
historic_data_url = "https://api.tdameritrade.com/v1/marketdata/"


def get_initial_universe():
    yahoo_screeners = ['day_gainers', 'most_actives']
    yahoo_page_keys = ['?offset=0&count=100', '?count=100&offset=100', '?count=100&offset=200']

    list_of_dataframes = []
    for i in yahoo_screeners:
        for x in yahoo_page_keys:
            df = pd.read_html(f'{yahoo_url}{i}')[0]
            list_of_dataframes.append(df)

    df = pd.concat(list_of_dataframes)
    df.drop_duplicates(keep='first', inplace=True)
    return(df)

stock_data = get_initial_universe()  
stock_data = stock_data.loc[(stock_data['Price (intraday)'] >= 4)]
stock_data = stock_data.loc[(stock_data['Price (intraday)'] <= 50)]
ticker_list = [ticker for ticker in stock_data['Symbol']]

with open(f"C:\\Users\\lm44\\Documents\\Code\\Pyhton\\Trading\\Trading Algo 2\\Screener Results\\{date.today()}.csv", 'w') as myfile:
     myfile.write(f'Initial tickers ({len(ticker_list)}): \n{ticker_list}')


def get_historic_data():
    time_series_data = TimeSeries(alphavantage_key, output_format='pandas')   
    dict_of_dataframes = {}
    for ticker in ticker_list:
        data = time_series_data.get_daily(symbol=ticker, outputsize='full')
        data = data[0].iloc[::-1].reset_index(drop=True)
        dict_of_dataframes.update({ticker:data})
        time.sleep(12.000001)
    return(dict_of_dataframes)

dict_of_dataframes = get_historic_data()

