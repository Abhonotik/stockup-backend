import yfinance as yf

def get_live_stock_price(symbol):
    try:
        stock = yf.Ticker(symbol)
        price = stock.history(period="1d")['Close'].iloc[-1]
        return round(price, 2)
    except Exception as e:
        return None
    



import yfinance as yf

def fetch_stock_info(query):
    stock = yf.Ticker(query)
    info = stock.info
    return {
        'symbol': query,
        'name': info.get('longName', query)
    }

# Example:
print(fetch_stock_info('TCS.NS'))

