from django.shortcuts import render
from utils.permissions import role_required

@role_required(['admin', 'doctor'])
def patient_list(request):
    return render(request, 'patients/patient_list.html')