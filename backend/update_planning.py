import os
import django

# Provide the setup necessary to run Django models from a shell if needed, but here we just rewrite the files using AST/regex or simple replacements.

planning_models_path = "backend/planning/models.py"

with open(planning_models_path, "a") as f:
    f.write('''

import uuid
class Plan(models.Model):
    """Crop Plan as requested by the Product Spec"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="plans")
    field = models.ForeignKey(
        'field.FieldData',
        on_delete=models.CASCADE,
        related_name="plans",
    )
    crop_type = models.CharField(max_length=100)
    start_date = models.DateField(db_index=True)
    estimated_harvest_date = models.DateField(db_index=True)
    
    STATUS_CHOICES = [
        ("PLANNED", "Planned"),
        ("ACTIVE", "Active"),
        ("COMPLETED", "Completed"),
        ("FAILED", "Failed"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PLANNED")
    risk_score = models.FloatField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.crop_type} on {self.field.name} ({self.status})"
''')

print("planning/models.py updated.")
