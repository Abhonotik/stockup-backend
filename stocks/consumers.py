import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Portfolio
from .services import get_live_stock_price
from decimal import Decimal
from datetime import date

class DashboardConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope["user"].is_authenticated:
            await self.accept()
        else:
            await self.close()

    async def receive(self, text_data):
        user = self.scope["user"]
        portfolios = Portfolio.objects.filter(user=user, quantity__gt=0).select_related('stock')

        net_worth = Decimal('0')
        todays_pnl = Decimal('0')
        alerts = []
        today = date.today()

        for p in portfolios:
            latest_price = get_live_stock_price(p.stock.symbol) or p.average_price
            net_worth += p.quantity * latest_price

        data = {
            "net_worth": float(net_worth),
            "todays_pnl": float(todays_pnl),
            "alerts": alerts or ["No alerts for today!"],
        }

        await self.send(json.dumps(data))
