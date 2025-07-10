import csv
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from stocks.models import Stock

class Command(BaseCommand):
    help = 'Import stocks from EQUITY_L.csv'

    def handle(self, *args, **kwargs):
        csv_path = os.path.join(settings.BASE_DIR, 'stocks', 'EQUITY_L.csv')

        try:
            with open(csv_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                count = 0

                for row in reader:
                    symbol = row['SYMBOL'].strip() + '.NS'
                    name = row['NAME OF COMPANY'].strip()

                    stock, created = Stock.objects.get_or_create(symbol=symbol, defaults={'name': name})

                    if created:
                        count += 1
                        self.stdout.write(self.style.SUCCESS(f'Added: {symbol} - {name}'))
                    else:
                        self.stdout.write(f'Skipped (already exists): {symbol}')

                self.stdout.write(self.style.SUCCESS(f'\n✅ Imported {count} new stocks successfully.'))

        except FileNotFoundError:
            self.stderr.write(f'❌ File not found: {csv_path}')
