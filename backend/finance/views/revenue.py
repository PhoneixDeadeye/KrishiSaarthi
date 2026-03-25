"""
Revenue management API views.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from config.pagination import get_optional_paginator

from ..models import Revenue
from ..serializers import RevenueSerializer


class RevenueView(APIView):
    """
    GET /finance/revenue - List revenue entries
    POST /finance/revenue - Add revenue entry
    PUT /finance/revenue/{id} - Update revenue entry
    DELETE /finance/revenue/{id} - Delete revenue entry
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk=None):
        if pk:
            try:
                revenue = Revenue.objects.get(pk=pk, user=request.user)
                return Response(RevenueSerializer(revenue).data)
            except Revenue.DoesNotExist:
                return Response({'error': 'Revenue entry not found'}, status=status.HTTP_404_NOT_FOUND)
        
        queryset = Revenue.objects.filter(user=request.user).select_related('field', 'season').order_by('-date')
        
        field_id = request.query_params.get('field_id')
        if field_id:
            queryset = queryset.filter(field_id=field_id)
        
        season_id = request.query_params.get('season_id')
        if season_id:
            queryset = queryset.filter(season_id=season_id)

        paginator = get_optional_paginator(request)
        if paginator is not None:
            page = paginator.paginate_queryset(queryset, request)
            serializer = RevenueSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        serializer = RevenueSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = RevenueSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        try:
            revenue = Revenue.objects.get(pk=pk, user=request.user)
        except Revenue.DoesNotExist:
            return Response({'error': 'Revenue entry not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = RevenueSerializer(revenue, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            revenue = Revenue.objects.get(pk=pk, user=request.user)
            revenue.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Revenue.DoesNotExist:
            return Response({'error': 'Revenue entry not found'}, status=status.HTTP_404_NOT_FOUND)
