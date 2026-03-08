"""
Labor entry views for tracking worker wages.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from ..models import LaborEntry
from ..serializers import LaborEntrySerializer


class LaborEntryView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk=None):
        """List labor entries with optional filters"""
        if pk:
            entry = get_object_or_404(LaborEntry, pk=pk, user=request.user)
            serializer = LaborEntrySerializer(entry)
            return Response(serializer.data)
        
        entries = LaborEntry.objects.filter(user=request.user).select_related('field').order_by('-date')
        
        # Filter by field
        field_id = request.query_params.get('field_id')
        if field_id:
            entries = entries.filter(field_id=field_id)
        
        # Filter by date range
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        if start_date:
            entries = entries.filter(date__gte=start_date)
        if end_date:
            entries = entries.filter(date__lte=end_date)
        
        # Filter by payment status
        is_paid = request.query_params.get('is_paid')
        if is_paid is not None:
            entries = entries.filter(is_paid=is_paid == 'true')
        
        serializer = LaborEntrySerializer(entries, many=True)
        
        # Calculate summary
        total_wages = entries.aggregate(total=Sum('total_wage'))['total'] or 0
        unpaid_wages = entries.filter(is_paid=False).aggregate(total=Sum('total_wage'))['total'] or 0
        
        return Response({
            'entries': serializer.data,
            'summary': {
                'total_entries': entries.count(),
                'total_wages': float(total_wages),
                'unpaid_wages': float(unpaid_wages),
            }
        })
    
    def post(self, request):
        """Create a new labor entry"""
        serializer = LaborEntrySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, pk=None):
        """Update a labor entry"""
        entry = get_object_or_404(LaborEntry, pk=pk, user=request.user)
        serializer = LaborEntrySerializer(entry, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk=None):
        """Delete a labor entry"""
        entry = get_object_or_404(LaborEntry, pk=pk, user=request.user)
        entry.delete()
        return Response({'message': 'Entry deleted'}, status=status.HTTP_200_OK)
