"""
Inventory views for tracking farm supplies.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db import models
from django.db.models import Sum, F
from ..models import InventoryItem, InventoryTransaction
from ..serializers import InventoryItemSerializer, InventoryTransactionSerializer


class InventoryItemView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk=None):
        """List all inventory items or get single item"""
        if pk:
            item = get_object_or_404(InventoryItem, pk=pk, user=request.user)
            serializer = InventoryItemSerializer(item)
            return Response(serializer.data)
        
        items = InventoryItem.objects.filter(user=request.user).order_by('category', 'name')
        
        # Filter by category
        category = request.query_params.get('category')
        if category:
            items = items.filter(category=category)
        
        # Filter low stock items
        low_stock = request.query_params.get('low_stock')
        if low_stock == 'true':
            from django.db.models import F
            items = items.filter(quantity__lte=F('reorder_level'))
        
        serializer = InventoryItemSerializer(items, many=True)
        
        # Add summary data
        all_items = InventoryItem.objects.filter(user=request.user)
        response_data = {
            'items': serializer.data,
            'summary': {
                'total_items': all_items.count(),
                'low_stock_count': all_items.filter(
                    quantity__lte=models.F('reorder_level')
                ).count(),
            }
        }
        return Response(response_data)
    
    def post(self, request):
        """Create a new inventory item"""
        serializer = InventoryItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, pk=None):
        """Update an inventory item"""
        item = get_object_or_404(InventoryItem, pk=pk, user=request.user)
        serializer = InventoryItemSerializer(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk=None):
        """Delete an inventory item"""
        item = get_object_or_404(InventoryItem, pk=pk, user=request.user)
        item.delete()
        return Response({'message': 'Item deleted'}, status=status.HTTP_200_OK)


class InventoryTransactionView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, item_id=None):
        """List transactions for an inventory item"""
        if item_id:
            item = get_object_or_404(InventoryItem, pk=item_id, user=request.user)
            transactions = item.transactions.select_related('item').all()
        else:
            transactions = InventoryTransaction.objects.filter(item__user=request.user).select_related('item')
        
        serializer = InventoryTransactionSerializer(transactions, many=True)
        return Response(serializer.data)
    
    def post(self, request, item_id=None):
        """Add a transaction to an inventory item"""
        if item_id:
            item = get_object_or_404(InventoryItem, pk=item_id, user=request.user)
            data = request.data.copy()
            data['item'] = item_id
        else:
            data = request.data
            # Verify item belongs to user
            item = get_object_or_404(InventoryItem, pk=data.get('item'), user=request.user)
        
        serializer = InventoryTransactionSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            # Return updated item data
            item_serializer = InventoryItemSerializer(item)
            return Response({
                'transaction': serializer.data,
                'item': item_serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
