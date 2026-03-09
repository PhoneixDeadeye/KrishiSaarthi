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
        constraints = [
            models.CheckConstraint(
                check=models.Q(quantity__gte=0),
                name='inventory_quantity_non_negative',
            ),
        ]
    
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
    date = models.DateField(db_index=True)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date', '-created_at']
    
    def save(self, *args, **kwargs):
        # Update item quantity on transaction using F() to avoid race condition
        if not self.pk:  # New transaction
            from django.db.models import F
            if self.transaction_type in ['purchase', 'return']:
                InventoryItem.objects.filter(pk=self.item_id).update(
                    quantity=F('quantity') + self.quantity
                )
            elif self.transaction_type == 'use':
                # Check stock availability before deducting
                self.item.refresh_from_db()
                if self.item.quantity < self.quantity:
                    from django.core.exceptions import ValidationError
                    raise ValidationError(
                        f"Insufficient stock: available {self.item.quantity} {self.item.unit}, "
                        f"requested {self.quantity} {self.item.unit}"
                    )
                InventoryItem.objects.filter(pk=self.item_id).update(
                    quantity=F('quantity') - self.quantity
                )
            self.item.refresh_from_db()
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
    
    date = models.DateField(db_index=True)
    notes = models.TextField(blank=True)
    is_paid = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date']
        verbose_name_plural = 'Labor entries'
    
    def save(self, *args, **kwargs):
        # Always recalculate total_wage from hours * rate
        if self.hours_worked is not None and self.hourly_rate is not None:
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
        constraints = [
            models.CheckConstraint(
                check=models.Q(end_datetime__gt=models.F('start_datetime')),
                name='booking_end_after_start',
            ),
        ]

    def clean(self):
        """Validate no overlapping bookings for the same equipment."""
        from django.core.exceptions import ValidationError
        if self.start_datetime and self.end_datetime:
            if self.end_datetime <= self.start_datetime:
                raise ValidationError("End datetime must be after start datetime.")
            overlapping = EquipmentBooking.objects.filter(
                equipment=self.equipment,
                is_completed=False,
                start_datetime__lt=self.end_datetime,
                end_datetime__gt=self.start_datetime,
            ).exclude(pk=self.pk)
            if overlapping.exists():
                raise ValidationError(
                    f"Equipment '{self.equipment.name}' is already booked during this period."
                )

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.equipment.name} for {self.purpose} ({self.start_datetime.date()})"
