"""
Planning module serializers for KrishiSaarthi.
"""
from rest_framework import serializers
from .models import (
    SeasonCalendar, InventoryItem, InventoryTransaction,
    LaborEntry, Equipment, EquipmentBooking
)


class SeasonCalendarSerializer(serializers.ModelSerializer):
    activity_type_display = serializers.CharField(source='get_activity_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    field_name = serializers.CharField(source='field.name', read_only=True)
    
    class Meta:
        model = SeasonCalendar
        fields = [
            'id', 'field', 'field_name', 'title', 'activity_type', 'activity_type_display',
            'description', 'start_date', 'end_date', 'status', 'status_display', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class InventoryTransactionSerializer(serializers.ModelSerializer):
    transaction_type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)
    item_name = serializers.CharField(source='item.name', read_only=True)
    unit = serializers.CharField(source='item.unit', read_only=True)
    
    class Meta:
        model = InventoryTransaction
        fields = [
            'id', 'item', 'item_name', 'field', 'transaction_type', 'transaction_type_display',
            'quantity', 'unit', 'date', 'notes', 'created_at'
        ]
        read_only_fields = ['created_at']


class InventoryItemSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)
    recent_transactions = serializers.SerializerMethodField()
    
    class Meta:
        model = InventoryItem
        fields = [
            'id', 'name', 'category', 'category_display', 'description',
            'quantity', 'unit', 'reorder_level', 'is_low_stock',
            'purchase_price', 'supplier', 'created_at', 'updated_at', 'recent_transactions'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_recent_transactions(self, obj):
        # Only fetch 5 most recent at DB level, not all then slice in Python
        txns = obj.transactions.select_related('item').order_by('-created_at')[:5]
        return InventoryTransactionSerializer(txns, many=True).data


class LaborEntrySerializer(serializers.ModelSerializer):
    field_name = serializers.CharField(source='field.name', read_only=True)
    
    class Meta:
        model = LaborEntry
        fields = [
            'id', 'field', 'field_name', 'worker_name', 'work_type',
            'hours_worked', 'hourly_rate', 'total_wage', 'date',
            'notes', 'is_paid', 'created_at'
        ]
        read_only_fields = ['total_wage', 'created_at']


class EquipmentBookingSerializer(serializers.ModelSerializer):
    field_name = serializers.CharField(source='field.name', read_only=True)
    equipment_name = serializers.CharField(source='equipment.name', read_only=True)
    
    class Meta:
        model = EquipmentBooking
        fields = [
            'id', 'equipment', 'equipment_name', 'field', 'field_name',
            'start_datetime', 'end_datetime', 'purpose', 'notes',
            'is_completed', 'created_at'
        ]
        read_only_fields = ['created_at']


class EquipmentSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    upcoming_bookings = serializers.SerializerMethodField()
    
    class Meta:
        model = Equipment
        fields = [
            'id', 'name', 'equipment_type', 'description',
            'purchase_date', 'purchase_price', 'status', 'status_display',
            'last_maintenance', 'created_at', 'upcoming_bookings'
        ]
        read_only_fields = ['created_at']
    
    def get_upcoming_bookings(self, obj):
        # Fetch only 3 most recent at DB level instead of loading all then slicing
        bookings = obj.bookings.select_related('field').order_by('start_datetime')[:3]
        return EquipmentBookingSerializer(bookings, many=True).data

