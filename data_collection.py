import pandas as pd
import yfinance as yf


stocks = ['AAPL','AMZN','GOOGL','META','NFLX','JPM','GS','MS','BAC','NVDA','TSM','MSFT','PLTR']

data = yf.download(stocks, start = '2022-01-01', end = '2025-09-21')['Close']

#print(data.head())

print("missing data:")
print(data.isna().sum())
data.to_csv('stock_data.csv')