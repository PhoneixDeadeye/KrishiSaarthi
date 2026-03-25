"""
Season management API views.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db.models import Sum
from config.pagination import get_optional_paginator

from ..models import Season
from ..serializers import SeasonSerializer


class SeasonView(APIView):
    """
    GET /finance/seasons - List seasons
    POST /finance/seasons - Create season
    PUT /finance/seasons/{id} - Update season
    DELETE /finance/seasons/{id} - Delete season
    """
    permission_classes = [permissions.IsAuthenticated]

    def _annotated_queryset(self, qs):
        """Annotate queryset with aggregate totals to avoid N+1 in serializer."""
        return qs.annotate(
            _total_costs=Sum('costs__amount'),
            _total_revenue=Sum('revenues__total_amount'),
        )

    def get(self, request, pk=None):
        if pk:
            try:
                season = self._annotated_queryset(
                    Season.objects.filter(pk=pk, user=request.user)
                ).get()
                return Response(SeasonSerializer(season).data)
            except Season.DoesNotExist:
                return Response({'error': 'Season not found'}, status=status.HTTP_404_NOT_FOUND)
        
        queryset = Season.objects.filter(user=request.user).select_related('field')
        
        field_id = request.query_params.get('field_id')
        if field_id:
            queryset = queryset.filter(field_id=field_id)
        
        is_active = request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        queryset = self._annotated_queryset(queryset)
        paginator = get_optional_paginator(request)
        if paginator is not None:
            page = paginator.paginate_queryset(queryset, request)
            serializer = SeasonSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        serializer = SeasonSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = SeasonSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        try:
            season = Season.objects.get(pk=pk, user=request.user)
        except Season.DoesNotExist:
            return Response({'error': 'Season not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = SeasonSerializer(season, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            season = Season.objects.get(pk=pk, user=request.user)
            season.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Season.DoesNotExist:
            return Response({'error': 'Season not found'}, status=status.HTTP_404_NOT_FOUND)
