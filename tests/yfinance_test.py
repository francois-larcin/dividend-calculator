import yfinance as yf

aapl = yf.Ticker("MSFT")

info = aapl.info

print(info.dividends.tail(10))
