from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from .forms import * # Importación de los formularios
from .forms import Patient, LoginForm
from exam.models import Exam
from django.conf import settings
from django.contrib import messages
from .forms import UploadFileForm, AddPatientForm # Importación de los formularios
from exam.utils.generate_analysis import generate_analysis_pdf
import pandas as pd
from datetime import datetime
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

# Create your views here.
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
    searchTerm = request.GET.get('searchPatient', '')
    if searchTerm:
        files = Exam.objects.filter(patient__name__icontains = searchTerm)
        
    else:
        files = Exam.objects.all()
    return render(request, 'home.html', {'searchTerm':searchTerm, 'files':files})

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
            exam.analysis_date = datetime.now()
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