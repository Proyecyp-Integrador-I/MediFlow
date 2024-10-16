from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from .forms import * # Importación de los formularios
from .forms import Exam, Patient, LoginForm
from django.conf import settings
from django.contrib import messages
from .forms import UploadFileForm, AddPatientForm # Importación de los formularios
from mediflowApp.utils.generate_analysis import generate_analysis_pdf
from django.conf import settings

from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

from mediflowApp.utils.send_email import send_email

from PyPDF2 import PdfReader, PdfWriter
import os
import pandas as pd
import pdfplumber
import re
import io
import datetime

def login_view(request):
    error_message = ""
    if request.method == 'POST':
        error_message = "Dirección de correo o contraseña incorrectos."
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # Autenticamos el usuario
            user = authenticate(email=email, password=password)

            if user is not None:
                auth_login(request, user)

                # Verificamos si es staff o superuser
                if user.is_superuser or user.is_staff:
                    return redirect('/administrator')  # Redirige a la vista del administrador
                else:
                    return redirect('/')  # Redirige al home o vista regular
            else:
                return render(request, 'login.html', {'form': form, 'error_message': error_message})
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form, 'error_message': error_message})

def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def home(request):
    files = Exam.objects.all() # Filter by user
    return render(request, 'home.html', {'files':files})

@login_required
def search(request):
    
    Patient.objects.all().delete()
    Exam.objects.all().delete()
    searchTerm = request.GET.get('searchPatient', '')
    if searchTerm:
        files = Patient.objects.filter(name__icontains=searchTerm)
    else:
        files = Patient.objects.all()
    return render(request, 'home.html', {'searchTerm':searchTerm, 'file':files})


def calculate_age(birthdate):
    today = datetime.datetime.today()
    age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
    return age

def text_extraction(file_content):
        with pdfplumber.open(io.BytesIO(file_content)) as pdf:
            first_page = pdf.pages[0]
            text = first_page.extract_text()
            id = re.search("(?<=ID:)\s?[0-9]*", text)
            name = re.search("(?<=Name:)\s?.* .*, \w+|(?<=Nombre:)\s?.* .*, .*?(?=OD|OS)", text)
            birthdate = re.search("(?<=DOB:)\s?..-...-..|(?<=Fecha de nacimiento:)\s?[0-9]{1,2}/[0-9]{2}/[0-9]{4}", text)
            exam_date = re.search("(?<=Exam Date:)\s?..-...-..|(?<=Fecha de examen:)\s?[0-9]{1,2}/[0-9]{2}/[0-9]{4}", text)
            gender = re.search("(?<=Gender:)\s?\w+|(?<=Sexo:)\s?\w+", text)
            name = name.group().strip() if name else ''
            id = id.group().strip() if id else ''
            birthdate = birthdate.group().strip() if birthdate else ''
            exam_date = exam_date.group().strip() if exam_date else ''
            gender = gender.group().strip() if gender else ''

            try:
                birthdate = datetime.datetime.strptime(birthdate, '%d-%b-%y').date() if birthdate else None
                exam_date = datetime.datetime.strptime(exam_date, '%d-%b-%y').date() if exam_date else None
            except:
                try:
                    birthdate = datetime.datetime.strptime(birthdate, '%d/%m/%Y').date() if birthdate else None
                    exam_date = datetime.datetime.strptime(exam_date, '%d/%m/%Y').date() if exam_date else None
                except:
                    birthdate = None
                    exam_date = None

            last_name = name.split(", ")[0] if name else ''
            name = name.split(", ")[1] if name else ''

            return {
                "id": id,
                "name": name,
                "last_name": last_name,
                "birthdate": birthdate,
                "exam_date": exam_date,
                "gender": gender
            }

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
    print("No POST")
    return render(request, 'new_exam.html')

@login_required
def new_patient(request):
    if request.method == 'POST':
        form = AddPatientForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Patient created successfully!')
            return redirect("home") # Redirigir a una página de éxito
        else:
            messages.error(request, 'Something went wrong. Please verify and try again.')
    else:
        form = AddPatientForm()
    return render(request, 'new_patient.html', {'form': form})

@login_required
def automated_patient_extraction(request):
    if request.method == 'POST':
        try:
            patient_list = request.FILES.get('patient_list')
            df = pd.read_excel(patient_list)

            df.columns = df.columns.str.strip()
            for index, row in df.iterrows():
                existing_patient = Patient.objects.filter(identification=row['Identificación']).exists()
                if not existing_patient:
                    patient = Patient(
                        name=row['Nombre del paciente'],
                        last_name="",
                        identification=row['Identificación'],
                        age=row['Edad'],
                        health_insurance=row['Entidad'])
                    patient.save()
        except Exception as e:
            return render(request, 'automated_extraction.html', {'error': "Error al procesar el archivo"})

        return redirect("home") # Redirigir a una página de éxito
    else:
        return render(request, 'automated_extraction.html', {'error': ""})

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
    patient = exam.patient
    file_path = f'media/{exam.exam_type}_{patient.name}_{patient.last_name}.pdf'
    generate_analysis_pdf(exam, patient, file_path)

    exam.save()

    with open(file_path, "rb") as fh:
        response = HttpResponse(fh.read(), content_type="applicaction/pdf")
        response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
        return response

@login_required
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

@login_required
def view_pdf(request, pk):
    exam = get_object_or_404(Exam, pk=pk)
    default_analysis = ''
    if exam.exam_type.lower() == 'nervio óptico' and exam.is_analyzed == True: 
        default_analysis = '''CONCLUSIONES 

                            1.	Examen con buena confiabilidad en AO. 
                            2.	Ambos nervios ópticos son normales con excavación aumentada AO.
                            3.	Grosor normal en la capa de fibras nerviosas en AO con buena simetría AO.  
                            4.	Grosor normal en la capa de células ganglionares AO. 
                            5.	Se recomienda hacer correlación con el cuadro clínico del paciente y con otras ayudas diagnósticas.
                        '''
    if exam.exam_type.lower() == 'segmento anterior' and exam.is_analyzed == True: 
        default_analysis = '''CONCLUSIONES 

                            1.	Examen con buena confiabilidad en AO. 
                            2.	Ambos nervios ópticos son normales con excavación aumentada AO.
                            3.	Grosor normal en la capa de fibras nerviosas en AO con buena simetría AO.  
                            4.	Grosor normal en la capa de células ganglionares AO. 
                            5.	Se recomienda hacer correlación con el cuadro clínico del paciente y con otras ayudas diagnósticas.
                        '''
    if request.method == 'POST':
        form = UploadFileForm(request.POST, instance=exam)
        if form.is_valid():
            exam.result_analysis = request.POST.get('result_analysis')
            patient = exam.patient

            exam.is_analyzed = True  # Por ejemplo, marcar como analizado una vez se edite
            # Crear un PDF con el resultado del análisis
            pdf_path = f'media/{exam.exam_type}_{patient.name}_{patient.last_name}.pdf'
            generate_analysis_pdf(exam, patient, pdf_path)
            #exam.analyzed_path

            exam.save()
            """ response = HttpResponse(fh.read(), content_type="applicaction/pdf")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(pdf_path)
            return response """

            return redirect('download', path=pk)
    else:
        form = UploadFileForm(instance=exam)
    return render(request, 'view_pdf.html', {'form': form, 'file': exam, 'default_analysis': default_analysis})

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
