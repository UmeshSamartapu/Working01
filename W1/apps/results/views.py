from django.shortcuts import render
from utils.permissions import role_required

@role_required(['admin', 'doctor'])
def result_view(request):
    return render(request, 'results/result.html')