"""
Calendar views for season planning.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404
from ..models import SeasonCalendar
from ..serializers import SeasonCalendarSerializer


class SeasonCalendarView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """List calendar events for user, optionally filtered by field"""
        events = SeasonCalendar.objects.filter(user=request.user).select_related('field').order_by('start_date')
        
        field_id = request.query_params.get('field_id')
        if field_id:
            events = events.filter(field_id=field_id)
        
        # Filter by date range
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        if start_date:
            events = events.filter(end_date__gte=start_date)
        if end_date:
            events = events.filter(start_date__lte=end_date)
        
        # Filter by status
        event_status = request.query_params.get('status')
        if event_status:
            events = events.filter(status=event_status)
        
        serializer = SeasonCalendarSerializer(events, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        """Create a new calendar event"""
        serializer = SeasonCalendarSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, pk=None):
        """Update an existing calendar event"""
        event = get_object_or_404(SeasonCalendar, pk=pk, user=request.user)
        serializer = SeasonCalendarSerializer(event, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk=None):
        """Delete a calendar event"""
        event = get_object_or_404(SeasonCalendar, pk=pk, user=request.user)
        event.delete()
        return Response({'message': 'Event deleted'}, status=status.HTTP_200_OK)
