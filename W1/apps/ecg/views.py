from django.shortcuts import render, redirect
from .forms import ECGUploadForm
from utils.permissions import role_required

@role_required(['admin', 'technician'])
def upload_ecg(request):
    form = ECGUploadForm(request.POST or None, request.FILES or None)

    if request.method == 'POST' and form.is_valid():
        ecg = form.save(commit=False)
        ecg.uploaded_by = request.user
        ecg.save()

        return redirect('upload_ecg')  # reload page

    return render(request, 'ecg/upload_ecg.html', {'form': form})