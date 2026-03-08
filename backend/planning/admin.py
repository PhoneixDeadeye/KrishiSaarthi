from django.contrib import admin
from .models import (
    SeasonCalendar, InventoryItem, InventoryTransaction,
    LaborEntry, Equipment, EquipmentBooking
)


@admin.register(SeasonCalendar)
class SeasonCalendarAdmin(admin.ModelAdmin):
    list_display = ['title', 'field', 'activity_type', 'start_date', 'end_date', 'status']
    list_filter = ['activity_type', 'status', 'field']
    search_fields = ['title', 'description']
    raw_id_fields = ['user', 'field']
    date_hierarchy = 'start_date'


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'quantity', 'unit', 'reorder_level', 'is_low_stock', 'supplier']
    list_filter = ['category']
    search_fields = ['name', 'supplier']
    raw_id_fields = ['user']


@admin.register(InventoryTransaction)
class InventoryTransactionAdmin(admin.ModelAdmin):
    list_display = ['item', 'transaction_type', 'quantity', 'date', 'field']
    list_filter = ['transaction_type', 'date']
    raw_id_fields = ['item', 'field']
    date_hierarchy = 'date'


@admin.register(LaborEntry)
class LaborEntryAdmin(admin.ModelAdmin):
    list_display = ['worker_name', 'work_type', 'hours_worked', 'total_wage', 'date', 'is_paid', 'field']
    list_filter = ['is_paid', 'date', 'work_type']
    search_fields = ['worker_name']
    raw_id_fields = ['user', 'field']
    date_hierarchy = 'date'


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'equipment_type', 'status', 'last_maintenance', 'purchase_date']
    list_filter = ['status', 'equipment_type']
    search_fields = ['name']
    raw_id_fields = ['user']


@admin.register(EquipmentBooking)
class EquipmentBookingAdmin(admin.ModelAdmin):
    list_display = ['equipment', 'field', 'start_datetime', 'end_datetime', 'purpose', 'is_completed']
    list_filter = ['is_completed']
    raw_id_fields = ['equipment', 'field']
