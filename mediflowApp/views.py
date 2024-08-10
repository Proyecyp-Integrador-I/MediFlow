from django.shortcuts import render, redirect, get_object_or_404
from .forms import UploadFileForm # Importación de los formularios
from .forms import Exam
from .generate_analysis import generate_analysis_pdf

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
    file = get_object_or_404(Exam, pk=pk)
    if request.method == 'POST':
        form = UploadFileForm(request.POST, instance=file)
        if form.is_valid():
            file.result_analysis = request.POST.get('result_analysis')
            file.is_analyzed = True  # Por ejemplo, marcar como analizado una vez se edite

            # Crear un PDF con el resultado del análisis
            generate_analysis_pdf(file)
            
            file.save()

            return redirect('home')
    else:
        form = UploadFileForm(instance=file)
    return render(request, 'view_pdf.html', {'form': form, 'file': file})
