from django.urls import path, include
from rest_framework import routers
from .views import StockViewSet, TransactionViewSet, PortfolioViewSet, CapitalGainsViewSet, live_price, search_stocks, PortfolioSummaryView

router = routers.DefaultRouter()
router.register(r'stocks', StockViewSet)
router.register(r'transactions', TransactionViewSet)
router.register(r'portfolio', PortfolioViewSet)
router.register(r'capital-gains', CapitalGainsViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/live-price/<str:symbol>/', live_price, name='live-price'),
    path('api/search-stocks/', search_stocks, name='search-stocks'),
    path('api/portfolio/summary/', PortfolioSummaryView.as_view(), name='portfolio-summary'),


]
