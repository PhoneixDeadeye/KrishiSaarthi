from rest_framework import viewsets, permissions
from finance.models import FinanceTransaction
from finance.serializers import FinanceTransactionSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

class FinanceTransactionViewSet(viewsets.ModelViewSet):
    """
    CRUD API for FinanceTransactions.
    """
    serializer_class = FinanceTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['type', 'field', 'date']
    ordering_fields = ['date', 'amount', 'created_at']
    ordering = ['-date', '-created_at']

    def get_queryset(self):
        return FinanceTransaction.objects.filter(user=self.request.user).select_related('field')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
