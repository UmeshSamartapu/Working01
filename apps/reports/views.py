from django.shortcuts import render
from utils.permissions import role_required

@role_required(['admin', 'doctor'])
def report_view(request):
    return render(request, 'reports/report.html')