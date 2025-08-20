from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import User, Stock, Transaction, Portfolio, CapitalGains, Watchlist

admin.site.register(User)
admin.site.register(Stock)
admin.site.register(Transaction)
admin.site.register(Portfolio)
admin.site.register(CapitalGains)
admin.site.register(Watchlist)