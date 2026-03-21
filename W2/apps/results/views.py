from django.shortcuts import render
from apps.diagnosis.models import Diagnosis
from utils.permissions import role_required

@role_required(['admin', 'doctor'])
def result_view(request):
    diagnoses = Diagnosis.objects.all().order_by('-created_at')

    return render(request, 'results/result.html', {
        'diagnoses': diagnoses
    })