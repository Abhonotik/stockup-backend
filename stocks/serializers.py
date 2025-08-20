from rest_framework import serializers
from .models import User, Stock, Transaction, Portfolio, CapitalGains
from .services import get_live_stock_price
from rest_framework import serializers
from .models import Watchlist
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = '__all__'

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'
        read_only_fields = ['price', 'brokerage', 'stt', 'gst', 'sebi_charges', 'stamp_duty']

class PortfolioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Portfolio
        fields = '__all__'
class CapitalGainsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CapitalGains
        fields = '__all__'
                
# stocks/serializers.py

from .services import get_live_stock_price
class PortfolioSummarySerializer(serializers.ModelSerializer):
    stock_symbol = serializers.CharField(source='stock.symbol', read_only=True)
    stock_name = serializers.CharField(source='stock.name', read_only=True)
    current_price = serializers.SerializerMethodField()
    total_investment = serializers.SerializerMethodField()
    current_value = serializers.SerializerMethodField()
    unrealized_gain = serializers.SerializerMethodField()
    percentage_return = serializers.SerializerMethodField()

    class Meta:
        model = Portfolio
        fields = [
            'stock_symbol',
            'stock_name',
            'quantity',
            'average_price',
            'current_price',
            'total_investment',
            'current_value',
            'unrealized_gain',
            'percentage_return'
        ]
    
    def get_current_price(self, obj):
        price = get_live_stock_price(obj.stock.symbol, obj.stock.exchange)
        return round(price, 2) if price else 0

    def get_total_investment(self, obj):
        return round(float(obj.average_price) * float(obj.quantity), 2)

    def get_current_value(self, obj):
        current_price = self.get_current_price(obj)
        return round(current_price * float(obj.quantity), 2)

    def get_unrealized_gain(self, obj):
        return round(self.get_current_value(obj) - self.get_total_investment(obj), 2)

    def get_percentage_return(self, obj):
        investment = self.get_total_investment(obj)
        if investment == 0:
            return 0
        return round((self.get_unrealized_gain(obj) / investment) * 100, 2)

class WatchlistSerializer(serializers.ModelSerializer):
    stock_name = serializers.CharField(source='stock.name', read_only=True)
    symbol = serializers.CharField(source='stock.symbol', read_only=True)
    current_price = serializers.DecimalField(source='stock.current_price', max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Watchlist
        fields = ['id', 'symbol', 'stock_name', 'current_price', 'added_at']

class CapitalGainsSerializer(serializers.ModelSerializer):
    stock_symbol = serializers.CharField(source='stock.symbol', read_only=True)
    stock_name = serializers.CharField(source='stock.name', read_only=True)
    realized_gain = serializers.DecimalField(max_digits=15, decimal_places=2)
    short_term_gain = serializers.DecimalField(max_digits=15, decimal_places=2)
    long_term_gain = serializers.DecimalField(max_digits=15, decimal_places=2)
    tax_liability = serializers.DecimalField(max_digits=15, decimal_places=2)

    class Meta:
        model = CapitalGains
        fields = [
            'id',
            'stock_symbol',
            'stock_name',
            'realized_gain',
            'short_term_gain',
            'long_term_gain',
            'tax_liability'
        ]
