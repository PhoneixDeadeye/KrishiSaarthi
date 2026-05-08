import os

field_models_path = "backend/field/models.py"

with open(field_models_path, "a") as f:
    f.write('''

import uuid
class CropHealthScan(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="health_scans")
    field = models.ForeignKey(
        FieldData, on_delete=models.CASCADE, related_name="health_scans"
    )
    image_path = models.ImageField(upload_to="ml_scans/")
    detected_disease = models.CharField(max_length=100, blank=True, null=True)
    confidence_score = models.FloatField(blank=True, null=True)
    recommendation = models.TextField(blank=True, null=True)
    severity = models.CharField(max_length=20, default="LOW")
    
    scanned_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-scanned_at"]
        indexes = [
            models.Index(fields=["user", "field", "-scanned_at"]),
        ]

    def __str__(self):
        return f"{self.field.name} - {self.detected_disease} ({self.confidence_score})"
''')

print("field/models.py updated with CropHealthScan.")
