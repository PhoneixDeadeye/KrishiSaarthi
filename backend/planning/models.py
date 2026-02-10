"""
Planning module models for KrishiSaarthi.
Handles season planning, inventory tracking, labor management, and equipment scheduling.
"""
from django.db import models
from django.contrib.auth.models import User
from field.models import FieldData


class ActivityType(models.TextChoices):
    """Types of farm activities"""
    SOWING = 'sowing', 'Sowing'
    IRRIGATION = 'irrigation', 'Irrigation'
    FERTILIZING = 'fertilizing', 'Fertilizing'
    SPRAYING = 'spraying', 'Spraying'
    WEEDING = 'weeding', 'Weeding'
    HARVESTING = 'harvesting', 'Harvesting'
    OTHER = 'other', 'Other'


class ActivityStatus(models.TextChoices):
    """Status of planned activities"""
    PLANNED = 'planned', 'Planned'
    IN_PROGRESS = 'in_progress', 'In Progress'
    COMPLETED = 'completed', 'Completed'
    CANCELLED = 'cancelled', 'Cancelled'


class SeasonCalendar(models.Model):
    """Planned farm activities for season planning"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='calendar_events')
    field = models.ForeignKey(FieldData, on_delete=models.CASCADE, related_name='calendar_events')
    
    title = models.CharField(max_length=255)
    activity_type = models.CharField(max_length=20, choices=ActivityType.choices)
    description = models.TextField(blank=True)
    
    start_date = models.DateField()
    end_date = models.DateField()
    
    status = models.CharField(max_length=20, choices=ActivityStatus.choices, default=ActivityStatus.PLANNED)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['start_date']
        verbose_name_plural = 'Calendar events'
    
    def __str__(self):
        return f"{self.title} ({self.start_date} - {self.end_date})"


class InventoryCategory(models.TextChoices):
    """Categories for inventory items"""
    SEEDS = 'seeds', 'Seeds'
    FERTILIZER = 'fertilizer', 'Fertilizer'
    PESTICIDE = 'pesticide', 'Pesticide'
    HERBICIDE = 'herbicide', 'Herbicide'
    TOOLS = 'tools', 'Tools'
    OTHER = 'other', 'Other'


class InventoryItem(models.Model):
    """Farm inventory items like seeds, fertilizers, pesticides"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inventory_items')
    
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=20, choices=InventoryCategory.choices)
    description = models.TextField(blank=True)
    
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    unit = models.CharField(max_length=50)  # kg, liters, packets, etc.
    reorder_level = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    supplier = models.CharField(max_length=255, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['category', 'name']
    
    @property
    def is_low_stock(self):
        return self.quantity <= self.reorder_level
    
    def __str__(self):
        return f"{self.name} ({self.quantity} {self.unit})"


class TransactionType(models.TextChoices):
    """Types of inventory transactions"""
    PURCHASE = 'purchase', 'Purchase'
    USE = 'use', 'Use'
    ADJUSTMENT = 'adjustment', 'Adjustment'
    RETURN = 'return', 'Return'


class InventoryTransaction(models.Model):
    """Track inventory usage and purchases"""
    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name='transactions')
    field = models.ForeignKey(FieldData, on_delete=models.SET_NULL, null=True, blank=True, related_name='inventory_transactions')
    
    transaction_type = models.CharField(max_length=20, choices=TransactionType.choices)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date', '-created_at']
    
    def save(self, *args, **kwargs):
        # Update item quantity on transaction
        if not self.pk:  # New transaction
            if self.transaction_type in ['purchase', 'return']:
                self.item.quantity += self.quantity
            elif self.transaction_type == 'use':
                self.item.quantity -= self.quantity
            self.item.save()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.transaction_type}: {self.quantity} {self.item.unit} of {self.item.name}"


class LaborEntry(models.Model):
    """Track labor/worker costs"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='labor_entries')
    field = models.ForeignKey(FieldData, on_delete=models.CASCADE, related_name='labor_entries')
    
    worker_name = models.CharField(max_length=255)
    work_type = models.CharField(max_length=100)  # Sowing, weeding, harvesting, etc.
    
    hours_worked = models.DecimalField(max_digits=5, decimal_places=2)
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2)
    total_wage = models.DecimalField(max_digits=10, decimal_places=2)
    
    date = models.DateField()
    notes = models.TextField(blank=True)
    is_paid = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date']
        verbose_name_plural = 'Labor entries'
    
    def save(self, *args, **kwargs):
        if not self.total_wage:
            self.total_wage = self.hours_worked * self.hourly_rate
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.worker_name}: ₹{self.total_wage} ({self.date})"


class EquipmentStatus(models.TextChoices):
    """Equipment availability status"""
    AVAILABLE = 'available', 'Available'
    IN_USE = 'in_use', 'In Use'
    MAINTENANCE = 'maintenance', 'Under Maintenance'
    RETIRED = 'retired', 'Retired'


class Equipment(models.Model):
    """Farm equipment registry"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='equipment')
    
    name = models.CharField(max_length=255)
    equipment_type = models.CharField(max_length=100)  # Tractor, pump, sprayer, etc.
    description = models.TextField(blank=True)
    
    purchase_date = models.DateField(null=True, blank=True)
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=EquipmentStatus.choices, default=EquipmentStatus.AVAILABLE)
    last_maintenance = models.DateField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Equipment'
    
    def __str__(self):
        return f"{self.name} ({self.equipment_type})"


class EquipmentBooking(models.Model):
    """Equipment usage scheduling"""
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='bookings')
    field = models.ForeignKey(FieldData, on_delete=models.CASCADE, related_name='equipment_bookings')
    
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    purpose = models.CharField(max_length=255)
    notes = models.TextField(blank=True)
    
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['start_datetime']
    
    def __str__(self):
        return f"{self.equipment.name} for {self.purpose} ({self.start_datetime.date()})"
