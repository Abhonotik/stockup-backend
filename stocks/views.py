from django.shortcuts import render
from django.db import models
from decimal import Decimal

from rest_framework import viewsets
from .models import Stock, Transaction, Portfolio, CapitalGains
from .serializers import StockSerializer, TransactionSerializer, PortfolioSerializer, CapitalGainsSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly

# Stocks CRUD
class StockViewSet(viewsets.ModelViewSet):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

# Calculate charges safely using Decimal
def calculate_charges(transaction):
    amount = Decimal(str(transaction.price)) * Decimal(str(transaction.quantity))

    brokerage = min(Decimal('20'), Decimal('0.0003') * amount)
    stt = Decimal('0.001') * amount
    gst = Decimal('0.18') * brokerage
    sebi = Decimal('10') / Decimal('10000000') * amount
    stamp = Decimal('0.00003') * amount if transaction.transaction_type == 'BUY' else Decimal('0')

    transaction.brokerage = round(brokerage, 2)
    transaction.stt = round(stt, 2)
    transaction.gst = round(gst, 2)
    transaction.sebi_charges = round(sebi, 2)
    transaction.stamp_duty = round(stamp, 2)

    transaction.save()

from .services import get_live_stock_price

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        stock = serializer.validated_data['stock']
        stock_symbol = stock.symbol

        # ✅ Fetch live price (fallback to 0)
        live_price = get_live_stock_price(stock_symbol) or 0

        # ✅ Save transaction with user + live price
        transaction = serializer.save(user=self.request.user, price=live_price)

        # ✅ Calculate charges (STT, etc.)
        calculate_charges(transaction)

        # ✅ Update portfolio
        update_portfolio(
            user=transaction.user,
            stock=transaction.stock,
            transaction_type=transaction.transaction_type,
            quantity=transaction.quantity,
            price=transaction.price
        )

        # ✅ Capital Gains for SELL
        if transaction.transaction_type == 'SELL':
            portfolio = Portfolio.objects.filter(user=transaction.user, stock=transaction.stock).first()
            avg_price = portfolio.average_price if portfolio else 0

            update_capital_gains(
                user=transaction.user,
                stock=transaction.stock,
                quantity_sold=transaction.quantity,
                sell_price=transaction.price,
                buy_price=avg_price,
                sell_date=transaction.date
            )

            process_sell_with_fifo(
                user=transaction.user,
                stock=transaction.stock,
                quantity_sold=transaction.quantity,
                sell_price=transaction.price,
                sell_date=transaction.date
            )

    


class PortfolioViewSet(viewsets.ModelViewSet):
    queryset = Portfolio.objects.all()
    serializer_class = PortfolioSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class CapitalGainsViewSet(viewsets.ModelViewSet):
    queryset = CapitalGains.objects.all()
    serializer_class = CapitalGainsSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

from .models import Portfolio

def update_portfolio(user, stock, transaction_type, quantity, price):
    portfolio, created = Portfolio.objects.get_or_create(user=user, stock=stock, defaults={
        'quantity': Decimal('0'),
        'average_price': Decimal('0')
    })

    quantity = Decimal(str(quantity))
    price = Decimal(str(price))

    if transaction_type == 'BUY':
        total_quantity = portfolio.quantity + quantity
        total_cost = (portfolio.average_price * portfolio.quantity) + (price * quantity)

        portfolio.quantity = total_quantity
        portfolio.average_price = total_cost / total_quantity if total_quantity != Decimal('0') else Decimal('0')

    elif transaction_type == 'SELL':
        portfolio.quantity -= quantity
        if portfolio.quantity < Decimal('0'):
            portfolio.quantity = Decimal('0')

    portfolio.save()

from .models import CapitalGains

def update_capital_gains(user, stock, quantity_sold, sell_price, buy_price, sell_date):
    quantity_sold = Decimal(str(quantity_sold))
    sell_price = Decimal(str(sell_price))
    buy_price = Decimal(str(buy_price))

    gain_per_unit = sell_price - buy_price
    total_gain = gain_per_unit * quantity_sold

    is_short_term = True  # Placeholder logic

    capital_gains, created = CapitalGains.objects.get_or_create(user=user, stock=stock, defaults={
        'realized_gain': Decimal('0'),
        'short_term_gain': Decimal('0'),
        'long_term_gain': Decimal('0'),
        'tax_liability': Decimal('0'),
    })

    capital_gains.realized_gain += total_gain

    if is_short_term:
        capital_gains.short_term_gain += total_gain
    else:
        capital_gains.long_term_gain += total_gain

    short_term_tax = Decimal('0.15') * capital_gains.short_term_gain
    long_term_tax = Decimal('0.10') * capital_gains.long_term_gain

    capital_gains.tax_liability = short_term_tax + long_term_tax

    capital_gains.save()

from rest_framework.decorators import api_view
from rest_framework.response import Response
from .services import get_live_stock_price

@api_view(['GET'])
def live_price(request, symbol):
    price = get_live_stock_price(symbol)
    if price is not None:
        return Response({'symbol': symbol, 'current_price': price})
    else:
        return Response({'error': 'Unable to fetch price'}, status=400)


def search_stocks(request):
    query = request.GET.get('q', '').strip()

    if not query:
        return Response({'error': 'Please provide a search query.'}, status=400)

    stocks = Stock.objects.filter(
        models.Q(name__icontains=query) | models.Q(symbol__icontains=query)
    )[:20]  # Limit to top 20 results for performance

    serializer = StockSerializer(stocks, many=True)
    return Response(serializer.data)


# stocks/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView
from .models import Portfolio
from .serializers import PortfolioSummarySerializer

class PortfolioSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        portfolios = Portfolio.objects.filter(user=request.user, quantity__gt=0)
        serializer = PortfolioSummarySerializer(portfolios, many=True)
        return Response(serializer.data)


class PortfolioSummaryView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PortfolioSummarySerializer

    def get_queryset(self):
        return Portfolio.objects.filter(user=self.request.user)
    
from decimal import Decimal
from datetime import datetime

def process_sell_with_fifo(user, stock, quantity_sold, sell_price, sell_date):
    buys = Transaction.objects.filter(
        user=user,
        stock=stock,
        transaction_type='BUY',
        quantity__gt=0
    ).order_by('date')  # FIFO: oldest first

    remaining_quantity = quantity_sold
    total_gain = Decimal('0.00')
    short_term_gain = Decimal('0.00')
    long_term_gain = Decimal('0.00')

    for buy in buys:
        if remaining_quantity <= 0:
            break

        available_qty = min(buy.quantity, remaining_quantity)
        buy_price = Decimal(buy.price)
        gain_per_unit = Decimal(sell_price) - buy_price
        gain = gain_per_unit * available_qty

        holding_period = (sell_date - buy.date).days
        if holding_period < 365:
            short_term_gain += gain
        else:
            long_term_gain += gain

        total_gain += gain
        remaining_quantity -= available_qty
        buy.quantity -= available_qty  # reduce quantity of the buy transaction
        buy.save()

    # Update Capital Gains record
    cap, _ = CapitalGains.objects.get_or_create(user=user, stock=stock)
    cap.realized_gain += total_gain
    cap.short_term_gain += short_term_gain
    cap.long_term_gain += long_term_gain
    cap.tax_liability = cap.short_term_gain * Decimal('0.15') + cap.long_term_gain * Decimal('0.10')
    cap.save()
