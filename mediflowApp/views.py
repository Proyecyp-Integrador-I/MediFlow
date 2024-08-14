from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from .forms import UploadFileForm # Importación de los formularios
from .forms import Exam
from .generate_analysis import generate_analysis_pdf
import os

def home(request):
    files = Exam.objects.all()
    return render(request, 'home.html', {'files': files})

def new_exam(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("home") # Redirigir a una página de éxito
    else:
        form = UploadFileForm()
    return render(request, 'new_exam.html', {'form': form})

def view_pdf(request, pk):
    exam = get_object_or_404(Exam, pk=pk)
    if request.method == 'POST':
        form = UploadFileForm(request.POST, instance=exam)
        if form.is_valid():
            exam.result_analysis = request.POST.get('result_analysis')
            exam.is_analyzed = True  # Por ejemplo, marcar como analizado una vez se edite

            # Crear un PDF con el resultado del análisis
            generate_analysis_pdf(exam, f'media/analysis_{exam.id}.pdf')

            exam.save()

            return redirect('home')
    else:
        form = UploadFileForm(instance=exam)
    return render(request, 'view_pdf.html', {'form': form, 'file': exam})

def download_file(request, Exam):
    file = get_object_or_404(generate_analysis_pdf.output_file, id=Exam.id)
    file_path = file.file.path
    file_name = os.path.basename(file_path)


    with open(file_path, 'rb') as f:
        response = HttpResponse(f.read(),content_type = 'application/force-download')
        response['Content-Disposition'] = f'attatchment; filename={file_name}'
        return response