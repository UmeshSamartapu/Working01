from django.db import models
from apps.patients.models import Patient

class ECGRecord(models.Model):
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='ecg_records'   # ✅ FIXED
    )

    uploaded_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE
    )

    file = models.FileField(upload_to='ecg_files/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"ECG {self.id} - {self.patient.name}"