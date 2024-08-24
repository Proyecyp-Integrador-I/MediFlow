from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from .forms import UploadFileForm, UploadExamForm, AddPatientForm # Importación de los formularios
from .forms import Exam, Patient
from .generate_analysis import generate_analysis_pdf
from django.conf import settings
import os

def home(request):
    files = Exam.objects.all() # Filter by user
    return render(request, 'home.html', {'files': files})

def new_exam(request):
    if request.method == 'POST':
        form = UploadExamForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("home") # Redirigir a una página de éxito
    else:
        form = UploadExamForm()
    return render(request, 'new_exam.html', {'form': form})

def new_patient(request):
    if request.method == 'POST':
        form = AddPatientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("home") # Redirigir a una página de éxito
    else:
        form = AddPatientForm()
    return render(request, 'new_patient.html', {'form': form})

def download(request, path):
    #generate_analysis_pdf(exam, patient, f'media/analysis_{exam.id}.pdf')
    #file_path = os.path.join(settings.MEDIA_ROOT, f'analysis_{path}.pdf')

    exam = get_object_or_404(Exam, pk=path)
    exam.result_analysis = exam.result_analysis
    exam.is_analyzed = True
    patient = exam.patient
    file_path = f'media/{exam.exam_type}_{patient.name}_{patient.last_name}.pdf'
    generate_analysis_pdf(exam, patient, file_path)
    exam.save()

    with open(file_path, "rb") as fh:
        response = HttpResponse(fh.read(), content_type="applicaction/pdf")
        response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
        return response




"""     if not os.path.exists(file_path):
            exam = get_object_or_404(Exam, pk=path)
            exam.result_analysis = request.POST.get('result_analysis')
            exam.is_analyzed = True
            patient = exam.patient
            generate_analysis_pdf(exam, patient, f'media/{exam.exam_type}_{patient.name}_{patient.last_name}.pdf')
            exam.save()
    with open(file_path, "rb") as fh:
        response = HttpResponse(fh.read(), content_type="applicaction/pdf")
        response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
        return response
 """

def next_exam(request):
    if request.method == 'POST':
        next_exams = Exam.objects.filter(is_analyzed=False)
        next_exam = next_exams.first()
        if next_exam:
            return redirect('view_pdf', pk=next_exam.id)
        else:
            return redirect('home')
    else:
        return render(request, 'next_exam.html')

def view_pdf(request, pk):
    exam = get_object_or_404(Exam, pk=pk)
    if request.method == 'POST':
        form = UploadFileForm(request.POST, instance=exam)
        if form.is_valid():
            exam.result_analysis = request.POST.get('result_analysis')
            exam.is_analyzed = True  # Por ejemplo, marcar como analizado una vez se edite
            patient = exam.patient
            # Crear un PDF con el resultado del análisis
            pdf_path = f'media/{exam.exam_type}_{patient.name}_{patient.last_name}.pdf'
            generate_analysis_pdf(exam, patient, pdf_path)

            exam.save()
            """ response = HttpResponse(fh.read(), content_type="applicaction/pdf")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(pdf_path)
            return response """

            return redirect('download', path=pk)
    else:
        form = UploadFileForm(instance=exam)
    return render(request, 'view_pdf.html', {'form': form, 'file': exam})