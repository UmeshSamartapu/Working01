from django.db import models
from apps.ecg.models import ECGRecord


class Diagnosis(models.Model):
    ecg = models.ForeignKey(
        ECGRecord,
        on_delete=models.CASCADE,
        related_name='diagnoses'
    )

    result = models.CharField(max_length=50)   # Normal / Arrhythmia
    predicted_class = models.CharField(max_length=100)  # model class
    confidence = models.FloatField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.result} ({self.confidence:.2f}%)"