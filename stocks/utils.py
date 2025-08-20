from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import yfinance as yf

def get_live_stock_price(symbol, exchange='NSE'):
    try:
        suffix = '.NS' if exchange.upper() == 'NSE' else '.BO'
        ticker = yf.Ticker(symbol + suffix)
        data = ticker.history(period="1d")
        if not data.empty:
            price = float(data['Close'].iloc[-1])
            
            # Notify dashboard via WebSocket
            send_dashboard_update(symbol, price)
            return price
        else:
            print(f"No data returned for {symbol}{suffix}")
    except Exception as e:
        print(f"Error fetching price for {symbol} ({exchange}): {e}")
    return 0.0


def send_dashboard_update(symbol, price):
    layer = get_channel_layer()
    async_to_sync(layer.group_send)(
        f"stocks",  # Your WebSocket group name
        {
            "type": "send_update",
            "message": {"symbol": symbol, "price": price}
        }
    )
