import yfinance as yf

msft = yf.Ticker("MELI")

info = msft.info

print(info.get('currentPrice'))
print(info.get('recommendationKey'))
