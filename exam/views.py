from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from .forms import * # Importación de los formularios
from .models import Exam, Patient
from django.conf import settings
from django.contrib import messages
from .forms import UploadExamForm # Importación de los formularios
from exam.utils.generate_analysis import generate_analysis_pdf
from exam.utils.send_email import send_email
from exam.utils.text_extraction import text_extraction, extract_multiple, concatenate_pdf, add_excel_info
from exam.utils.calculate_age import calculate_age
from PyPDF2 import PdfReader, PdfWriter
import os
import json
from datetime import datetime
from django.contrib.auth.decorators import login_required

from django.views.decorators.csrf import csrf_exempt
from django.conf import settings


from django.middleware.csrf import get_token

MEDIA_ROOT = settings.MEDIA_ROOT

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
                if birthdate != '':
                    patient = Patient(name=name, last_name=last_name, identification=identification, age=age, date_of_birth=birthdate, gender=gender)
                else:
                    patient = Patient(name=name, last_name=last_name, identification=identification, age=age, gender=gender)
                patient.save()

            if birthdate != '':
                exam = Exam(patient=patient, exam_date=exam_date, file=files[0])            
            else:
                exam = Exam(patient=patient, file=files[0])
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
                "date": exam.exam_date.isoformat() if exam.exam_date else None,
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
            health_insurance = request.POST.get('patient_health', "")

            date = request.POST.get('exam_date', old_exam["date"])

            exam_type = request.POST.get('exam_type', old_exam["exam_type"])
            file = old_exam["file"]
            apparatus = request.POST.get('apparatus', "")

            patient = Patient(name=name, last_name=last_name, identification=identification, age=age, date_of_birth=date_of_birth, gender=gender, health_insurance=health_insurance)
            patient.save()
            exam = Exam(patient=patient, exam_date=date, file=file, exam_type=exam_type, apparatus=apparatus)
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
def bulk_insertion(request):
    if request.method == 'POST':
        files = request.FILES.getlist('examFolders')
        csv_file = request.FILES.get('patientCSV')
        folder_structure = request.POST.get('folderStructure')
        csrf_token = get_token(request)
        print(csrf_token)

        folder_structure = json.loads(folder_structure)
        patient_folders = {}

        for element in folder_structure:
            
            folder = '/'.join(element['path'].split('/')[0:-1])
            file = element['path'].split('/')[-1]
            uploaded_file = next((f for f in files if f.name == file), None)
            print(folder, file, uploaded_file)

            if folder not in patient_folders:
                patient_folders[folder] = [uploaded_file]
            else:
                patient_folders[folder].append(uploaded_file)

        print(patient_folders)
        failed_patients = []

        for folder in patient_folders.keys():
            patient_info = extract_multiple(patient_folders[folder])
            print(patient_info)
            exam_file_name = f"{patient_info['name']} {patient_info['last_name']} {patient_info['exam_date'].strftime('%Y-%m-%d')}.pdf"
            exam_path = os.path.join(MEDIA_ROOT,"uploads", exam_file_name)
            if os.path.exists(exam_path):
                print("File already exists")
            else:
                concatenate_pdf(patient_folders[folder], exam_path)
                if not patient_info['id']:
                    failed_patients.append(patient_info)
                else:
                    patient = Patient.objects.filter(identification=patient_info['id']).first()
                    if not patient:
                        patient = Patient(
                                name=patient_info.get('name', None),
                                last_name=patient_info.get('last_name', None),
                                identification=patient_info.get('id', None), 
                                age=calculate_age(patient_info.get('birthdate')) if patient_info.get('birthdate') else None,
                                date_of_birth=patient_info.get('birthdate', None),
                                gender=patient_info.get('gender', None)
                            )
                        patient.save()
                    exam = Exam(patient=patient, exam_date=patient_info['exam_date'], file=exam_path)
                    exam.save()
                    print(exam)
        
        #add_excel_info(csv_file)

        print(failed_patients)
        return redirect("home") # Redirigir a una página de éxito
    return render(request, 'bulk_insertion.html')

@login_required
def download(request, path):
    exam = get_object_or_404(Exam, pk=path)
    exam.result_analysis = exam.result_analysis
    exam.is_analyzed = True
    exam.analysis_date = datetime.now()
    patient = exam.patient
    exam_date = exam.exam_date.strftime('%d/%m/%Y')
    
    file_path = f'media/{exam.exam_type}_{patient.name}_{patient.last_name}_{exam.exam_date}.pdf'
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
