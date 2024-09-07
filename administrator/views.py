from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from .forms import * # Importación de los formularios
from .forms import *
from django.conf import settings
from django.contrib import messages

def administrator(request):
    patients = Patient.objects.all()
    files = Exam.objects.all() # Filter by user
    doctors = Ophthalmologist.objects.all()
    return render(request, 'administrator.html', {'patients': patients, 'files': files, 'doctors': doctors})

def new_ophthalmologist(request):
    if request.method == 'POST':
        form = AddOphthalmologistForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ophthalmologist created successfully!')
            return redirect("administrator")
        else:
            messages.error(request, 'Something went wrong. Please verify and try again.')
    else:
        form = AddOphthalmologistForm()
    return render(request, 'new_ophthalmologist.html', {'form': form})

def delete_ophthalmologist(request, medical_license):
    if request.method == 'POST':
        ophthalmologist = Ophthalmologist.objects.filter(medical_license=medical_license).first()
        if ophthalmologist:
            ophthalmologist.delete()
            messages.success(request, f'Ophthalmologist with medical license {medical_license} deleted successfully!')
        else:
            messages.error(request, f'Ophthalmologist with medical license {medical_license} not found.')
        return redirect('administrator')

    return redirect('administrator')

def delete_patient(request, identification):
    if request.method == 'POST':
        patient = Patient.objects.filter(identification=identification).first()
        if patient:
            patient.delete()
            messages.success(request, f'Patient with ID {identification} deleted successfully!')
        else:
            messages.error(request, f'Patient with ID {identification} not found.')
        return redirect('administrator')

    return redirect('administrator')

def edit_ophthalmologist(request, medical_license):
    doctor = get_object_or_404(Ophthalmologist, medical_license=medical_license)
    
    if request.method == 'POST':
        form = EditOphthalmologistForm(request.POST, instance=doctor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ophthalmologist updated successfully!')
            return redirect('administrator')
        else:
            messages.error(request, 'Something went wrong. Please verify and try again.')
    else:
        form = EditOphthalmologistForm(instance=doctor)
    
    return render(request, 'edit_ophthalmologist.html', {'form': form})

def edit_patient(request, identification):
    patient = get_object_or_404(Patient, identification=identification)
    
    if request.method == 'POST':
        form = EditPatientForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            messages.success(request, 'Patient updated successfully!')
            return redirect('administrator')
        else:
            messages.error(request, 'Something went wrong. Please verify and try again.')
    else:
        form = EditPatientForm(instance=patient)
    
    return render(request, 'edit_patient.html', {'form': form})
