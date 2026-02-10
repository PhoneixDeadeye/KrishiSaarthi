"""
Cost Calculator API views.
Allows farmers to track input costs per field.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db.models import Sum, Count
from django.db.models.functions import Coalesce
from decimal import Decimal

from ..models import CostEntry, CostCategory
from ..serializers import CostEntrySerializer, CostSummarySerializer


class CostEntryView(APIView):
    """
    GET /finance/costs - List costs (optionally filter by field_id, season_id)
    POST /finance/costs - Add new cost entry
    PUT /finance/costs/{id} - Update cost entry
    DELETE /finance/costs/{id} - Delete cost entry
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk=None):
        if pk:
            try:
                cost = CostEntry.objects.get(pk=pk, user=request.user)
                return Response(CostEntrySerializer(cost).data)
            except CostEntry.DoesNotExist:
                return Response({'error': 'Cost entry not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Filter by field and/or season
        queryset = CostEntry.objects.filter(user=request.user)
        
        field_id = request.query_params.get('field_id')
        if field_id:
            queryset = queryset.filter(field_id=field_id)
        
        season_id = request.query_params.get('season_id')
        if season_id:
            queryset = queryset.filter(season_id=season_id)
        
        category = request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        serializer = CostEntrySerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CostEntrySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        try:
            cost = CostEntry.objects.get(pk=pk, user=request.user)
        except CostEntry.DoesNotExist:
            return Response({'error': 'Cost entry not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = CostEntrySerializer(cost, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            cost = CostEntry.objects.get(pk=pk, user=request.user)
            cost.delete()
            return Response({'message': 'Cost entry deleted'}, status=status.HTTP_200_OK)
        except CostEntry.DoesNotExist:
            return Response({'error': 'Cost entry not found'}, status=status.HTTP_404_NOT_FOUND)


class CostSummaryView(APIView):
    """
    GET /finance/costs/summary - Get cost breakdown by category
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        queryset = CostEntry.objects.filter(user=request.user)
        
        # Apply filters
        field_id = request.query_params.get('field_id')
        if field_id:
            queryset = queryset.filter(field_id=field_id)
        
        season_id = request.query_params.get('season_id')
        if season_id:
            queryset = queryset.filter(season_id=season_id)
        
        # Aggregate by category
        summary = queryset.values('category').annotate(
            total=Coalesce(Sum('amount'), Decimal('0')),
            count=Count('id')
        ).order_by('-total')
        
        # Add display names
        result = []
        for item in summary:
            result.append({
                'category': item['category'],
                'category_display': CostCategory(item['category']).label,
                'total': item['total'],
                'count': item['count']
            })
        
        total = queryset.aggregate(total=Coalesce(Sum('amount'), Decimal('0')))['total']
        
        return Response({
            'breakdown': result,
            'total': total
        })
