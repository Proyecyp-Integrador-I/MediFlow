from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from .forms import * # Importación de los formularios
from .models import Exam
from django.conf import settings
from django.contrib import messages
from .forms import UploadExamForm # Importación de los formularios
from exam.utils.generate_analysis import generate_analysis_pdf
from exam.utils.send_email import send_email
from exam.utils.text_extraction import text_extraction
from exam.utils.calculate_age import calculate_age
from PyPDF2 import PdfReader, PdfWriter
import os
from datetime import datetime
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
def new_exam(request):
    if request.method == 'POST':
        if 'new_exam' in request.POST:
            request.session.pop('patient_data', None)
            request.session.pop('exam_data', None)
            files = request.FILES.getlist('examFiles')

            if not files:
                messages.error(request, 'No files were uploaded')
                return redirect('new_exam')
            
            file_content = files[0].read()
            extracted_data = text_extraction(file_content)
            print(extracted_data)

            identification = extracted_data['id']
            birthdate = extracted_data['birthdate']
            exam_date = extracted_data['exam_date']
            gender = extracted_data['gender']
            name = extracted_data['name']
            last_name = extracted_data['last_name']

            if birthdate:
                age = calculate_age(birthdate)
            else:
                age = None
            
            existing_patient = Patient.objects.filter(identification=identification).first()
            if existing_patient:
                patient = existing_patient
            else:
                patient = Patient(name=name, last_name=last_name, identification=identification, age=age, date_of_birth=birthdate, gender=gender)
                patient.save()

            exam = Exam(patient=patient, date=exam_date, file=files[0])
            exam.save()

            exam_new  = exam
            patient_new = patient

            patient_data = {
                "name": patient.name,
                "last_name": patient.last_name,
                "identification": patient.identification,
                "age": patient.age,
                "date_of_birth": patient.date_of_birth.isoformat() if patient.date_of_birth else None,
                "gender": patient.gender
            }

            exam_data = {
                "id": exam.id,
                "date": exam.date.isoformat() if exam.date else None,
                "file": exam.file.name,
                "exam_type": exam.exam_type,
                "is_analyzed": exam.is_analyzed,
                "result_analysis": exam.result_analysis
            }

            exam.delete()
            patient.delete()

            request.session['patient_data'] = patient_data
            request.session['exam_data'] = exam_data

            print("Patient data: ", patient_data)
            print(request.session['patient_data'])
            print(request.session.get('patient_data'))

            return render(request, 'exam_form_valid.html', {'patient': patient_new, 'exam': exam_new})

        elif 'validate_exam' in request.POST:

            # Get the previous patient
            old_patient = request.session.get('patient_data')
            old_exam = request.session.get('exam_data')

            name = request.POST.get('patient_name', old_patient["name"])
            last_name = request.POST.get('patient_last_name', old_patient["last_name"])

            identification = request.POST.get('patient_id', old_patient["identification"])

            if identification == '':
                messages.error(request, 'Identification is required')
                return render(request, 'exam_form_valid.html', {'patient': old_patient, 'exam': old_exam})
            elif Patient.objects.filter(identification=identification).exists():
                print("Patient exists")
                messages.error(request, 'Identification already exists')
                return render(request, 'exam_form_valid.html', {'patient': old_patient, 'exam': old_exam})

            date_of_birth = request.POST.get('patient_DOB', old_patient["date_of_birth"])
            age = request.POST.get('patient_age', old_patient["age"])
            gender = request.POST.get('patient_gender', old_patient["gender"])

            date = request.POST.get('exam_date', old_exam["date"])

            exam_type = request.POST.get('exam_type', old_exam["exam_type"])
            file = old_exam["file"]

            patient = Patient(name=name, last_name=last_name, identification=identification, age=age, date_of_birth=date_of_birth, gender=gender)
            patient.save()
            exam = Exam(patient=patient, date=date, file=file, exam_type=exam_type)
            exam.save()
            print(exam.file.url)

            return redirect('home')
    return render(request, 'new_exam.html')


@login_required
def multiple_exams(request):
    if request.method == 'POST':
        patient_list = request.FILES.get('patient_list')
        if form.is_valid():
            form.save()
            return redirect("home") # Redirigir a una página de éxito
    else:
        form = UploadExamForm()
    return render(request, 'multiple_exams.html')

@login_required
def download(request, path):
    exam = get_object_or_404(Exam, pk=path)
    exam.result_analysis = exam.result_analysis
    exam.is_analyzed = True
    exam.analysis_date = datetime.now()
    patient = exam.patient
    file_path = f'media/{exam.exam_type}_{patient.name}_{patient.last_name}.pdf'
    generate_analysis_pdf(exam, patient, file_path)

    exam.save()

    with open(file_path, "rb") as fh:
        response = HttpResponse(fh.read(), content_type="applicaction/pdf")
        response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
        return response
    
def add_password_to_pdf(input_pdf, output_pdf, password):
    reader = PdfReader(input_pdf)
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    writer.encrypt(user_password=password)

    with open(output_pdf, 'wb') as output_file:
        writer.write(output_file)

def email_view(request, pk):
    exam = get_object_or_404(Exam, pk=pk)
    patient = exam.patient
    if request.method == 'POST':
        recipient = patient.email
        user_id = 1 # Hardcoded, cambiar a perfil del doctor
        subject = f'Resultado de OCT {exam.exam_type} - {patient.name} {patient.last_name}' # Cambiar a datos de la clinica
        body = '''Buenos días,
                  Adjunto encontrará el resultado de su examen de OCT.

                    Saludos cordiales,
                    [Nombre de la clínica]
                '''
        attachment_path = f'media/{exam.exam_type}_{patient.name}_{patient.last_name}.pdf'

        password = "hola"
        protected_attachment_path = f'media/protected_{exam.exam_type}_{patient.name}_{patient.last_name}.pdf'
        add_password_to_pdf(attachment_path, protected_attachment_path, password)

        result = send_email(user_id, recipient, subject, body, protected_attachment_path)
        if result["status"] == "success":
            messages.success(request, f'Email enviado exitosamente a {recipient}')
            return redirect('view_pdf', pk=pk)
        else:
            messages.warning(request, f'Error al enviar el email a {recipient}: {result["message"]}')
            return redirect('view_pdf', pk=pk)
    else:
        return redirect('view_pdf', pk=pk)
