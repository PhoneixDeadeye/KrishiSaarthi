"""
Finance module models for KrishiSaarthi.
Tracks costs, revenues, and profit/loss per field and season.
"""
from django.db import models
from django.contrib.auth.models import User
from field.models import FieldData


class Season(models.Model):
    """Growing season for grouping financial data"""
    SEASON_CHOICES = [
        ('kharif', 'Kharif (Monsoon)'),
        ('rabi', 'Rabi (Winter)'),
        ('zaid', 'Zaid (Summer)'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='seasons')
    name = models.CharField(max_length=100)
    season_type = models.CharField(max_length=20, choices=SEASON_CHOICES)
    year = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    field = models.ForeignKey(FieldData, on_delete=models.CASCADE, related_name='seasons')
    crop = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-year', '-start_date']
        unique_together = ['user', 'field', 'season_type', 'year']
    
    def __str__(self):
        return f"{self.name} - {self.season_type} {self.year}"


class CostCategory(models.TextChoices):
    """Categories for cost entries"""
    SEEDS = 'seeds', 'Seeds'
    FERTILIZER = 'fertilizer', 'Fertilizer'
    PESTICIDE = 'pesticide', 'Pesticide'
    LABOR = 'labor', 'Labor'
    IRRIGATION = 'irrigation', 'Irrigation'
    EQUIPMENT = 'equipment', 'Equipment Rental'
    TRANSPORT = 'transport', 'Transport'
    OTHER = 'other', 'Other'


class CostEntry(models.Model):
    """Individual cost entry for tracking expenses"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='costs')
    field = models.ForeignKey(FieldData, on_delete=models.CASCADE, related_name='costs')
    season = models.ForeignKey(Season, on_delete=models.SET_NULL, null=True, blank=True, related_name='costs')
    
    category = models.CharField(max_length=20, choices=CostCategory.choices)
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    unit = models.CharField(max_length=50, blank=True)  # e.g., kg, liters, hours
    
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date']
        verbose_name_plural = 'Cost entries'
        indexes = [
            models.Index(fields=['user', 'field', '-date']),
            models.Index(fields=['user', 'season', 'category']),
        ]
    
    def __str__(self):
        return f"{self.category}: ₹{self.amount} - {self.date}"


class Revenue(models.Model):
    """Revenue entry from crop sales"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='revenues')
    field = models.ForeignKey(FieldData, on_delete=models.CASCADE, related_name='revenues')
    season = models.ForeignKey(Season, on_delete=models.SET_NULL, null=True, blank=True, related_name='revenues')
    
    crop = models.CharField(max_length=100)
    quantity_sold = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=50, default='kg')
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    
    buyer = models.CharField(max_length=255, blank=True)  # Mandi name, trader, etc.
    date = models.DateField()
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date']
        indexes = [
            models.Index(fields=['user', 'field', '-date']),
            models.Index(fields=['user', 'crop']),
        ]

    def save(self, *args, **kwargs):
        # Always recalculate total from quantity and price when both are provided
        if self.quantity_sold is not None and self.price_per_unit is not None:
            self.total_amount = self.quantity_sold * self.price_per_unit
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.crop}: ₹{self.total_amount} - {self.date}"


class GovernmentScheme(models.Model):
    """Government subsidies and schemes database"""
    SCHEME_TYPES = [
        ('subsidy', 'Subsidy'),
        ('loan', 'Loan'),
        ('insurance', 'Insurance'),
        ('grant', 'Grant'),
        ('training', 'Training Program'),
    ]
    
    name = models.CharField(max_length=255)
    scheme_type = models.CharField(max_length=20, choices=SCHEME_TYPES)
    description = models.TextField()
    benefits = models.TextField(blank=True)
    eligible_crops = models.JSONField(default=list)  # ['Rice', 'Wheat', 'Cotton']
    eligible_states = models.JSONField(default=list)  # ['Punjab', 'Haryana', 'UP']
    min_land_acres = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    max_land_acres = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    max_subsidy_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    subsidy_percentage = models.IntegerField(null=True, blank=True)  # e.g., 50% subsidy
    application_deadline = models.DateField(null=True, blank=True)
    valid_from = models.DateField(null=True, blank=True)
    valid_until = models.DateField(null=True, blank=True)
    link = models.URLField(blank=True)
    documents_required = models.JSONField(default=list)  # ['Aadhaar', 'Land Records', 'Bank Passbook']
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-application_deadline', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.scheme_type})"


class InsuranceClaim(models.Model):
    """Crop insurance claim tracking (PMFBY - Pradhan Mantri Fasal Bima Yojana)"""
    DAMAGE_TYPES = [
        ('flood', 'Flood'),
        ('drought', 'Drought'),
        ('pest', 'Pest Attack'),
        ('disease', 'Crop Disease'),
        ('hail', 'Hailstorm'),
        ('fire', 'Fire'),
        ('other', 'Other Natural Calamity'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('paid', 'Paid'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='insurance_claims')
    field = models.ForeignKey(FieldData, on_delete=models.CASCADE, related_name='insurance_claims')
    season = models.ForeignKey(Season, on_delete=models.SET_NULL, null=True, blank=True, related_name='insurance_claims')
    
    policy_number = models.CharField(max_length=50, blank=True)
    crop = models.CharField(max_length=100)
    area_affected_acres = models.DecimalField(max_digits=8, decimal_places=2)
    damage_type = models.CharField(max_length=20, choices=DAMAGE_TYPES)
    damage_date = models.DateField()
    damage_description = models.TextField()
    estimated_loss = models.DecimalField(max_digits=12, decimal_places=2)
    claim_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    submitted_at = models.DateTimeField(null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewer_notes = models.TextField(blank=True)
    
    bank_account = models.CharField(max_length=20, blank=True)
    ifsc_code = models.CharField(max_length=11, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Claim #{self.id} - {self.crop} ({self.status})"
