# UserApp/models.py

from django.db import models
from django.contrib.auth.models import User


class ECGRecord(models.Model):
    uploaded_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="ecg_records"
    )

    filename = models.CharField(max_length=255)

    # 🔥 CRITICAL: ensures correct ordering of latest records
    uploaded_at = models.DateTimeField(auto_now_add=True, db_index=True)

    # Prediction output
    result = models.CharField(max_length=100, default="Unknown")
    confidence = models.FloatField(null=True, blank=True)

    # Health metrics
    risk_level = models.CharField(
        max_length=20,
        choices=[
            ("Low", "Low"),
            ("Medium", "Medium"),
            ("High", "High")
        ],
        default="Low"
    )

    bpm = models.IntegerField(null=True, blank=True)

    # Clinical interpretation
    affected_area = models.CharField(max_length=255, null=True, blank=True)
    affected_code = models.CharField(max_length=50, null=True, blank=True)

    # Files
    heart_image = models.ImageField(upload_to='heart_image/', null=True, blank=True)
    uploaded_file = models.ImageField(upload_to='uploads/', null=True, blank=True)

    # 🔥 Metadata for ordering + performance
    class Meta:
        ordering = ['-uploaded_at']   # always latest first
        indexes = [
            models.Index(fields=['-uploaded_at']),
        ]

    # 🔥 Helpful representation in admin/shell
    def __str__(self):
        return f"{self.result} | {self.risk_level} | {self.uploaded_at.strftime('%Y-%m-%d %H:%M:%S')}"