from django.core.management.base import BaseCommand
from stocks.models import Stock
import yfinance as yf
from decimal import Decimal

class Command(BaseCommand):
    help = 'Update current stock prices using yfinance'

    def handle(self, *args, **options):
        stocks = Stock.objects.all()
        updated_count = 0

        for stock in stocks:
            try:
                ticker = yf.Ticker(stock.symbol)
                price = ticker.history(period='1d')['Close'].iloc[-1]

                if price:
                    stock.current_price = Decimal(price)
                    stock.save()
                    updated_count += 1
                    self.stdout.write(self.style.SUCCESS(f"{stock.symbol} updated to {price}"))
                else:
                    self.stdout.write(self.style.WARNING(f"Price not found for {stock.symbol}"))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error updating {stock.symbol}: {str(e)}"))

        self.stdout.write(self.style.SUCCESS(f"\n✅ Updated {updated_count} stocks."))

