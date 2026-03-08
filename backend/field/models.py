from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class FieldData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='fields')
    name = models.CharField(max_length=100, default="My Field")
    cropType = models.CharField(max_length=32)
    polygon = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.name} ({self.cropType})"
    
class Pest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="pest/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.uploaded_at.strftime('%Y-%m-%d %H:%M:%S')}"


ACTIVITY_CHOICES = [
    ('Watering', 'Watering'),
    ('Fertilizer', 'Fertilizer'),
    ('Sowing', 'Sowing'),
    ('Pesticide', 'Pesticide'),
    ('Harvest', 'Harvest'),
    ('Other', 'Other'),
]

class FieldLog(models.Model):
    """Model for storing farm calendar/log entries"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='field_logs')
    field = models.ForeignKey(FieldData, on_delete=models.CASCADE, related_name='logs', null=True, blank=True)
    date = models.DateField(db_index=True)
    activity = models.CharField(max_length=20, choices=ACTIVITY_CHOICES)
    details = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.activity} on {self.date}"


class FieldAlert(models.Model):
    """Model for storing automated field alerts"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='field_alerts')
    field = models.ForeignKey(FieldData, on_delete=models.CASCADE, related_name='alerts', null=True, blank=True)
    log = models.ForeignKey(FieldLog, on_delete=models.CASCADE, related_name='alerts', null=True, blank=True)
    date = models.DateField(db_index=True)
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.user.username} - Alert on {self.date}"


class IrrigationSource(models.TextChoices):
    """Sources of irrigation water"""
    CANAL = 'canal', 'Canal'
    BOREWELL = 'borewell', 'Borewell'
    RAIN = 'rain', 'Rain'
    DRIP = 'drip', 'Drip System'
    SPRINKLER = 'sprinkler', 'Sprinkler'
    OTHER = 'other', 'Other'


class IrrigationLog(models.Model):
    """Log of actual irrigation events"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='irrigation_logs')
    field = models.ForeignKey(FieldData, on_delete=models.CASCADE, related_name='irrigation_logs')
    
    date = models.DateField(db_index=True)
    water_amount = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)  # liters or mm
    duration_minutes = models.PositiveIntegerField(null=True, blank=True)
    source = models.CharField(max_length=20, choices=IrrigationSource.choices, default=IrrigationSource.OTHER)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date', '-created_at']
    
    def __str__(self):
        return f"{self.field.name} - {self.date} ({self.source})"