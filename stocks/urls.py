from django.urls import path, include
from rest_framework import routers


from .views import (
    StockViewSet,
    TransactionViewSet,
    PortfolioViewSet,
    CapitalGainsViewSet,
    live_price,
    search_stocks,
    PortfolioSummaryView,
    DashboardView, 
)

from django.urls import path, include
from rest_framework import routers
from .views import (
    StockViewSet, 
    TransactionViewSet, 
    PortfolioViewSet, 
    CapitalGainsViewSet,
    live_price,
    search_stocks,
    PortfolioSummaryView,
    DashboardView
)

router = routers.DefaultRouter()
router.register(r'stocks', StockViewSet)
router.register(r'transactions', TransactionViewSet)
router.register(r'portfolio', PortfolioViewSet)
router.register(r'capital-gains', CapitalGainsViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('live-price/<str:symbol>/', live_price, name='live-price'),
    path('search-stocks/', search_stocks, name='search-stocks'),
    path('portfolio/summary/', PortfolioSummaryView.as_view(), name='portfolio-summary'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
]
