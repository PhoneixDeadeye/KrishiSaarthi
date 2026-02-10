"""
Finance module URL configuration.
"""
from django.urls import path
from .views import (
    CostEntryView, CostSummaryView, PnLDashboardView, SeasonView, RevenueView,
    PriceForecastView, SchemesView, SchemeDetailView,
    InsuranceClaimView, InsuranceClaimDetailView
)
from .views.market_prices import MarketPricesView

urlpatterns = [
    # Cost entries
    path('costs', CostEntryView.as_view(), name='costList'),
    path('costs/<int:pk>', CostEntryView.as_view(), name='costDetail'),
    path('costs/summary', CostSummaryView.as_view(), name='costSummary'),
    
    # Revenue entries
    path('revenue', RevenueView.as_view(), name='revenueList'),
    path('revenue/<int:pk>', RevenueView.as_view(), name='revenueDetail'),
    
    # Seasons
    path('seasons', SeasonView.as_view(), name='seasonList'),
    path('seasons/<int:pk>', SeasonView.as_view(), name='seasonDetail'),
    
    # P&L Dashboard
    path('pnl', PnLDashboardView.as_view(), name='pnlDashboard'),
    
    # Market Prices
    path('market-prices', MarketPricesView.as_view(), name='marketPrices'),
    
    # Price Forecast
    path('price-forecast', PriceForecastView.as_view(), name='priceForecast'),
    
    # Government Schemes
    path('schemes', SchemesView.as_view(), name='schemesList'),
    path('schemes/<int:scheme_id>', SchemeDetailView.as_view(), name='schemeDetail'),
    
    # Insurance Claims
    path('insurance', InsuranceClaimView.as_view(), name='insuranceList'),
    path('insurance/<int:claim_id>', InsuranceClaimDetailView.as_view(), name='insuranceDetail'),
]


