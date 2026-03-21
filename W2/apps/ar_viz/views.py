from django.shortcuts import render
from utils.permissions import role_required

@role_required(['admin', 'doctor'])
def ar_view(request):
    return render(request, 'ar_viz/ar.html')