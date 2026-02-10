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


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'quantity', 'unit', 'is_low_stock']
    list_filter = ['category']
    search_fields = ['name']


@admin.register(InventoryTransaction)
class InventoryTransactionAdmin(admin.ModelAdmin):
    list_display = ['item', 'transaction_type', 'quantity', 'date']
    list_filter = ['transaction_type', 'date']


@admin.register(LaborEntry)
class LaborEntryAdmin(admin.ModelAdmin):
    list_display = ['worker_name', 'work_type', 'hours_worked', 'total_wage', 'date', 'is_paid']
    list_filter = ['is_paid', 'date']
    search_fields = ['worker_name']


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'equipment_type', 'status', 'last_maintenance']
    list_filter = ['status', 'equipment_type']
    search_fields = ['name']


@admin.register(EquipmentBooking)
class EquipmentBookingAdmin(admin.ModelAdmin):
    list_display = ['equipment', 'field', 'start_datetime', 'end_datetime', 'is_completed']
    list_filter = ['is_completed']
