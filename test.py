import yfinance as yf
import datetime

symbol = 'RELIANCE.NS'
start = datetime.datetime(2024, 6, 17)
end = datetime.datetime(2024, 7, 17)

data = yf.download(symbol, start=start, end=end)
print(data.head())
print("Rows fetched:", len(data))
