from rest_framework import serializers
from .models import User, Stock, Transaction, Portfolio, CapitalGains

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
        price = get_live_stock_price(obj.stock.symbol)
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

