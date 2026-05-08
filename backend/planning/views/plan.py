from rest_framework import viewsets, permissions
from planning.models import Plan
from planning.serializers import PlanSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

class PlanViewSet(viewsets.ModelViewSet):
    """
    CRUD API for farm Plans.
    """
    serializer_class = PlanSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status', 'field']
    ordering_fields = ['start_date', 'estimated_harvest_date', 'risk_score']
    ordering = ['-start_date']

    def get_queryset(self):
        return Plan.objects.filter(user=self.request.user).select_related('field')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
