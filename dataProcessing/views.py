import os
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from .ocr import process_pdf
from mediflowApp.models import Exam

def ocr_view(request, id):
    exam = get_object_or_404(Exam, pk=id)
    
    pdf_path = os.path.join(settings.BASE_DIR, "media", exam.file.name)  

    results = process_pdf(pdf_path)
    return JsonResponse({'ocr_text': results})