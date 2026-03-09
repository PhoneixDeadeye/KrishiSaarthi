"""
P&L Dashboard API view.
Provides profit/loss analysis per field and season.
"""
import logging

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from django.db.models import Sum
from django.db.models.functions import Coalesce
from decimal import Decimal

from ..models import CostEntry, Revenue, Season, CostCategory

logger = logging.getLogger(__name__)


class PnLDashboardView(APIView):
    """
    GET /finance/pnl - Get profit/loss summary
    Query params: field_id, season_id
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            field_id = request.query_params.get('field_id')
            season_id = request.query_params.get('season_id')
            
            # Build cost queryset
            cost_qs = CostEntry.objects.filter(user=user)
            revenue_qs = Revenue.objects.filter(user=user)
            
            if field_id:
                cost_qs = cost_qs.filter(field_id=field_id)
                revenue_qs = revenue_qs.filter(field_id=field_id)
            
            if season_id:
                cost_qs = cost_qs.filter(season_id=season_id)
                revenue_qs = revenue_qs.filter(season_id=season_id)
            
            # Calculate totals
            total_costs = cost_qs.aggregate(
                total=Coalesce(Sum('amount'), Decimal('0'))
            )['total']
            
            total_revenue = revenue_qs.aggregate(
                total=Coalesce(Sum('total_amount'), Decimal('0'))
            )['total']
            
            profit_loss = total_revenue - total_costs
            
            # Profit margin calculation
            profit_margin = None
            if total_revenue > 0:
                profit_margin = (profit_loss / total_revenue) * 100
            
            # Cost breakdown by category
            cost_breakdown = cost_qs.values('category').annotate(
                total=Coalesce(Sum('amount'), Decimal('0'))
            ).order_by('-total')
            
            breakdown_list = [
                {
                    'category': item['category'],
                    'category_display': CostCategory(item['category']).label,
                    'total': float(item['total']),
                    'percentage': float(item['total'] / total_costs * 100) if total_costs > 0 else 0
                }
                for item in cost_breakdown
            ]
            
            # Revenue by crop
            revenue_by_crop = revenue_qs.values('crop').annotate(
                total=Coalesce(Sum('total_amount'), Decimal('0')),
                quantity=Sum('quantity_sold')
            ).order_by('-total')
            
            return Response({
                'summary': {
                    'total_costs': float(total_costs),
                    'total_revenue': float(total_revenue),
                    'profit_loss': float(profit_loss),
                    'profit_margin': float(profit_margin) if profit_margin else None,
                    'is_profitable': profit_loss > 0
                },
                'cost_breakdown': breakdown_list,
                'revenue_by_crop': list(revenue_by_crop),
                'filters': {
                    'field_id': field_id,
                    'season_id': season_id
                }
            })
        except Exception as exc:
            logger.error("P&L dashboard error: %s", exc, exc_info=True)
            return Response(
                {'error': 'Failed to load profit/loss data'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
