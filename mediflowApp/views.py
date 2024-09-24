from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from .forms import * # Importación de los formularios
from .forms import Exam, Patient, LoginForm
from django.conf import settings
from django.contrib import messages
from .forms import UploadFileForm, UploadExamForm, AddPatientForm # Importación de los formularios
from mediflowApp.utils.generate_analysis import generate_analysis_pdf
from django.conf import settings
from mediflowApp.utils.send_email import send_email
from PyPDF2 import PdfReader, PdfWriter
import os
import pandas as pd
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

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


#@login_required
def home(request):
    files = Exam.objects.all() # Filter by user
    searchTerm = request.GET.get('searchPatient')
    if searchTerm:
        patient = Patient.objects.filter(name__icontains='searchTerm')
    else:
        patient = Patient.objects.all()
    return render(request, 'home.html', {'searchTerm':searchTerm, 'Patient':patient, 'files':files})

@login_required
def new_exam(request):
    if request.method == 'POST':
        form = UploadExamForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("home") # Redirigir a una página de éxito
    else:
        form = UploadExamForm()
    return render(request, 'new_exam.html', {'form': form})

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
                print(index)
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
