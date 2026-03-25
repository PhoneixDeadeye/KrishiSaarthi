from datetime import timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from config.pagination import get_optional_paginator

from ..models import FieldLog, FieldAlert
from ..serializers import FieldLogSerializer, FieldAlertSerializer

# Activity -> Alert mapping (days until alert)
ACTIVITY_ALERT_DAYS = {
    'Watering': (2, 'Reminder: Water the crop again'),
    'Fertilizer': (5, 'Reminder: Apply fertilizer'),
    'Sowing': (3, 'Check irrigation for new sowing'),
    'Pesticide': (7, 'Check for pest outbreak'),
    'Harvest': (0, ''),
    'Other': (1, 'Follow-up activity'),
}


class FieldLogView(APIView):
    """CRUD API for field calendar logs"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get all logs for the authenticated user, optionally filtered by field"""
        field_id = request.query_params.get('field_id')
        if field_id:
            logs = FieldLog.objects.filter(user=request.user, field_id=field_id)
        else:
            logs = FieldLog.objects.filter(user=request.user)
        
        logs = logs.select_related('field').order_by('-date', '-created_at')
        paginator = get_optional_paginator(request)
        if paginator is not None:
            page = paginator.paginate_queryset(logs, request)
            serializer = FieldLogSerializer(page, many=True, context={'request': request})
            return paginator.get_paginated_response(serializer.data)
        serializer = FieldLogSerializer(logs, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        """Create a new field log entry"""
        serializer = FieldLogSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            # If field_id is passed in body, it's handled by serializer.
            # Access validated_data to get the field if needed or just save.
            log = serializer.save(user=request.user)
            
            # Create auto-alert if applicable
            activity = log.activity
            if activity in ACTIVITY_ALERT_DAYS:
                days, message = ACTIVITY_ALERT_DAYS[activity]
                if days > 0 and message:
                    alert_date = log.date + timedelta(days=days)
                    FieldAlert.objects.create(
                        user=request.user,
                        log=log,
                        date=alert_date,
                        message=message
                    )
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        """Delete a field log entry"""
        if not pk:
            return Response(
                {"error": "Log ID is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            log = FieldLog.objects.get(pk=pk, user=request.user)
            log.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except FieldLog.DoesNotExist:
            return Response(
                {"error": "Log not found"},
                status=status.HTTP_404_NOT_FOUND
            )


class FieldAlertView(APIView):
    """API for field alerts"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get all alerts for the authenticated user"""
        field_id = request.query_params.get('field_id')
        if field_id:
            alerts = FieldAlert.objects.filter(user=request.user, field_id=field_id)
        else:
            alerts = FieldAlert.objects.filter(user=request.user)
        
        alerts = alerts.select_related('field', 'log').order_by('-date', '-created_at')
        paginator = get_optional_paginator(request)
        if paginator is not None:
            page = paginator.paginate_queryset(alerts, request)
            serializer = FieldAlertSerializer(page, many=True, context={'request': request})
            return paginator.get_paginated_response(serializer.data)
        serializer = FieldAlertSerializer(alerts, many=True, context={'request': request})
        return Response(serializer.data)

    def patch(self, request, pk=None):
        """Mark a single alert as read, or mark all alerts read when pk='all'"""
        if pk == 'all':
            updated = FieldAlert.objects.filter(
                user=request.user, is_read=False
            ).update(is_read=True)
            return Response({'marked_read': updated})

        if not pk:
            return Response(
                {"error": "Alert ID is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            alert = FieldAlert.objects.get(pk=pk, user=request.user)
            alert.is_read = True
            alert.save()
            return Response(FieldAlertSerializer(alert, context={'request': request}).data)
        except FieldAlert.DoesNotExist:
            return Response(
                {"error": "Alert not found"},
                status=status.HTTP_404_NOT_FOUND
            )


class BulkMarkAlertsReadView(APIView):
    """Bulk mark unread alerts as read for the authenticated user."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        field_id = request.data.get('field_id') or request.query_params.get('field_id')
        alerts = FieldAlert.objects.filter(user=request.user, is_read=False)
        if field_id:
            alerts = alerts.filter(field_id=field_id)
        marked = alerts.update(is_read=True)
        return Response({'marked': marked}, status=status.HTTP_200_OK)
