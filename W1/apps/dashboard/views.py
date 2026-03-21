from django.shortcuts import render
from utils.permissions import role_required

def dashboard_home(request):
    return render(request, 'dashboard/home.html')


@role_required(['admin', 'doctor'])
def doctor_dashboard(request):
    return render(request, 'dashboard/doctor.html')


@role_required(['admin', 'technician'])
def technician_dashboard(request):
    return render(request, 'dashboard/technician.html')