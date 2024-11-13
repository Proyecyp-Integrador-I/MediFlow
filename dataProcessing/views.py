import os
from django.conf import settings
from django.shortcuts import get_object_or_404, render

from .ocr import process_pdf
from exam.models import Exam

def ocr_view(request, id):
    import re

    exam = get_object_or_404(Exam, pk=id)
    pdf_path = os.path.join(settings.BASE_DIR, "media", exam.file.name)

    # Procesar el PDF para obtener los resultados
    raw_results = process_pdf(pdf_path)

    # Dividir el texto en líneas y limpiar espacios en blanco
    formatted_results = []
    for result in raw_results:
        lines = result.split('\n')
        for line in lines:
            clean_line = line.strip()
            if clean_line:
                formatted_results.append(clean_line)

    # Convertir a una estructura clave-valor si hay un patrón
    structured_results = []
    for line in formatted_results:
        match = re.match(r"(.+?)\s+(\S+)$", line)
        if match:
            key, value = match.groups()
            structured_results.append({'label': key, 'value': value})
        else:
            structured_results.append({'label': line, 'value': ''})

    return render(request, 'exam_ocr.html', {'ocr_txt': structured_results})

def ocrs(request):
    exams = Exam.objects.all()
    return render(request, 'ocrs.html', {'exams': exams})