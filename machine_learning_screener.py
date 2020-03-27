from initial_universe import dict_of_dataframes
import numpy as np 
import math
from sklearn import preprocessing, svm
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from datetime import date, datetime 


def support_vector_regression():
    results = {}

    for ticker, df in dict_of_dataframes.items():
        
        df['Percent Change'] = ((df['4. close'] - df['1. open']) / df['1. open']) * 100
        df['High - Low'] = df['2. high'] - df['3. low']
        df = df[['4. close', '5. volume', 'Percent Change', 'High - Low']]
        df.dropna(inplace=True) 
        df = df.copy()

        forecast = '4. close'
        forecast_length = int(math.ceil( (len(df)/len(df)*5) ))
        df['label'] = df[forecast].shift(-forecast_length)        

        X = np.array(df.drop(['label'], 1))
        X = preprocessing.scale(X)
        X = X[:-forecast_length]
        df.dropna(inplace=True)
        df = df.copy()
        y = np.array(df['label'])

        X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.21, random_state=0)

        clf = svm.SVR()
        clf.fit(X_train, y_train)

        score = clf.score(X_test, y_test)

        if score > 0.9 and score < 1:
            results.update({ticker: df})
        

    return(results)

svm_tickers = [ticker for ticker, df in support_vector_regression().items()]
with open(f"C:\\Users\\lm44\\Documents\\Code\\Pyhton\\Trading\\Trading Algo 2\\Screener Results\\{date.today()}.csv", 'a') as myfile:
     myfile.write(f'SVM tickers ({len(svm_tickers)}): \n{svm_tickers}')


def linear_regression_screener():
    buy = []
    sell = []

    for ticker, df in support_vector_regression().items():

        forecast = '4. close'
        forecast_length = int(math.ceil( (len(df)/len(df)*5) ))
        df['label'] = df[forecast].shift(-forecast_length)

        X = np.array(df.drop(['label'], 1))
        X = preprocessing.scale(X)
        X_forecasted = X[-forecast_length:]
        X = X[:-forecast_length]
        df.dropna(inplace=True)
        df = df.copy()
        y = np.array(df['label'])

        X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=0)

        clf = LinearRegression()
        clf.fit(X_train, y_train)

        score = clf.score(X_test, y_test)
        forecasted_values = clf.predict(X_forecasted)

        five_day_projected_change = (float(forecasted_values[4]) - float(df['4. close'].iloc[-1]))/float(df['4. close'].iloc[-1]) * 100

        if score > 0.9 and score < 1 and five_day_projected_change >= 5 :
            buy.append(ticker)
        
        # elif score > 0.97 and score < 1 and five_day_projected_change <= -5 :
        #     sell.append(ticker)
        
    return(buy, sell)

buy_tickers = [ticker for ticker in linear_regression_screener()[0]]
sell_tickers = [ticker for ticker in linear_regression_screener()[1]]
tickers = buy_tickers + sell_tickers

with open(f"C:\\Users\\lm44\\Documents\\Code\\Pyhton\\Trading\\Trading Algo 2\\Screener Results\\{date.today()}.csv", 'a') as myfile:
     myfile.write(f'\nLinear Regression tickers ({len(tickers)}): \n{tickers}')
