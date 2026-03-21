from django.shortcuts import render, redirect, get_object_or_404
from .models import Patient
from .forms import PatientForm
from utils.permissions import role_required

@role_required(['admin', 'doctor'])
def patient_list(request):
    query = request.GET.get('q')

    if query:
        patients = Patient.objects.filter(name__icontains=query)
    else:
        patients = Patient.objects.all()

    return render(request, 'patients/patient_list.html', {'patients': patients})


@role_required(['admin', 'doctor'])
def add_patient(request):
    form = PatientForm(request.POST or None)

    if form.is_valid():
        patient = form.save(commit=False)
        patient.created_by = request.user
        patient.save()
        return redirect('patient_list')

    return render(request, 'patients/add_patient.html', {'form': form})


@role_required(['admin', 'doctor'])
def edit_patient(request, id):
    patient = get_object_or_404(Patient, id=id)
    form = PatientForm(request.POST or None, instance=patient)

    if form.is_valid():
        form.save()
        return redirect('patient_list')

    return render(request, 'patients/add_patient.html', {'form': form})


@role_required(['admin'])
def delete_patient(request, id):
    patient = get_object_or_404(Patient, id=id)
    patient.delete()
    return redirect('patient_list')