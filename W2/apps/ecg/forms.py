from django import forms
from .models import ECGRecord

class ECGUploadForm(forms.ModelForm):
    class Meta:
        model = ECGRecord
        fields = ['patient', 'file']