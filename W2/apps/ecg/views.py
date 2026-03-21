from django.shortcuts import render, redirect
from .forms import ECGUploadForm
from .models import ECGRecord
from utils.permissions import role_required


@role_required(['admin', 'technician', 'doctor'])
def upload_ecg(request):
    form = ECGUploadForm(request.POST or None, request.FILES or None)

    if form.is_valid():
        ecg = form.save(commit=False)
        ecg.uploaded_by = request.user
        ecg.save()

        return redirect('ecg_list')

    return render(request, 'ecg/upload_ecg.html', {'form': form})


@role_required(['admin', 'technician', 'doctor'])
def ecg_list(request):
    ecgs = ECGRecord.objects.all().order_by('-id')

    return render(request, 'ecg/ecg_list.html', {
        'ecgs': ecgs
    })