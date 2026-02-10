"""
Planning module URL configuration.
"""
from django.urls import path
from .views import (
    SeasonCalendarView, InventoryItemView, InventoryTransactionView,
    LaborEntryView, EquipmentView, EquipmentBookingView
)
from .views.rotation import RotationPlannerView

urlpatterns = [
    # Calendar events
    path('calendar', SeasonCalendarView.as_view(), name='calendarList'),
    path('calendar/<int:pk>', SeasonCalendarView.as_view(), name='calendarDetail'),
    
    # Inventory items
    path('inventory', InventoryItemView.as_view(), name='inventoryList'),
    path('inventory/<int:pk>', InventoryItemView.as_view(), name='inventoryDetail'),
    path('inventory/<int:item_id>/transaction', InventoryTransactionView.as_view(), name='inventoryTransaction'),
    path('transactions', InventoryTransactionView.as_view(), name='transactionList'),
    
    # Labor entries
    path('labor', LaborEntryView.as_view(), name='laborList'),
    path('labor/<int:pk>', LaborEntryView.as_view(), name='laborDetail'),
    
    # Equipment
    path('equipment', EquipmentView.as_view(), name='equipmentList'),
    path('equipment/<int:pk>', EquipmentView.as_view(), name='equipmentDetail'),
    path('equipment/<int:equipment_id>/book', EquipmentBookingView.as_view(), name='equipmentBook'),
    path('bookings', EquipmentBookingView.as_view(), name='bookingList'),
    path('bookings/<int:pk>', EquipmentBookingView.as_view(), name='bookingDetail'),
    
    # Rotation planner
    path('rotation', RotationPlannerView.as_view(), name='rotationPlanner'),
]

