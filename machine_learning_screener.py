from screen import *
import numpy as np 
import math
import pickle
from sklearn import preprocessing, svm
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split


tradeable_stocks = []

for df in historic_data:

    df['Percent Change'] = ((df['close'] - df['open']) / df['open']) * 100
    df['High - Low'] = df['high'] - df['low']
    df = df[['close', 'volume', 'Percent Change', 'High - Low']]
    df.dropna(inplace=True) 

    forecast = 'close'
    forecast_length = int(math.ceil( (len(df)/len(df)*5) ))
    df['label'] = df[forecast].shift(-forecast_length)

    X = np.array(df.drop(['label'], 1))
    X = preprocessing.scale(X)
    X = X[:-forecast_length]
    X_forecasted = X[-forecast_length:]
    df.dropna(inplace=True)
    y = np.array(df['label'])

    X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=0)

    pickle_in = open('linearregression.pickle', 'rb')
    clf = pickle.load(pickle_in)

    score = clf.score(X_test, y_test)
    forecasted_values = clf.predict(X_forecasted)

    print(score, forecasted_values)
    
    # if float(score) > 0.8: #change to be a certain percentage over the last price
    #     tradeable_stocks.append(df.index[0]) #find a more efficient way to get the related ticker

# print(tradeable_stocks)
