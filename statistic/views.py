from django.shortcuts import render
from mediflowApp.views import *
import matplotlib.pyplot as plt
from datetime import date
from io import BytesIO
import base64

# Create your views here.
def createStatistics(request):
    graphAges = patientByAge()
    return render(request, 'statistics.html', {'graphAges': graphAges})

def patientByAge():
    patients = Patient.objects.all()

    age_ranges = [
        (0, 9), (10, 19), (20, 29), (30, 39),
        (40, 49), (50, 59), (60, 69), (70, 79),
        (80, 89), (90, 100)
    ]

    age_counts = []

    today = date.today()

    for lower, upper in age_ranges:
        upper_date = today.replace(year=today.year - lower)
        lower_date = today.replace(year=today.year - (upper + 1))

        count = patients.filter(date_of_birth__gte=lower_date, date_of_birth__lt=upper_date).count()
        age_counts.append(count)

    age_labels = [f"{lower}-{upper}" for lower, upper in age_ranges]

    plt.rcParams['font.family'] = 'sans-serif'  # Usar 'sans-serif' para imitar la fuente de Bootstrap
    plt.rcParams['font.sans-serif'] = ['Helvetica', 'Arial']
    plt.figure(figsize=(10, 6))
    plt.bar(age_labels, age_counts, color='skyblue')
    #plt.title('Number of Patients by Age Range')
    plt.xlabel('Age Range')
    plt.ylabel('Number of Patients')
    plt.xticks()
    plt.ylim(0, None)
    plt.yticks(range(0, max(age_counts) + 1))
    ax = plt.gca()
    ax.spines['top'].set_visible(False)  # Ocultar la línea superior
    ax.spines['right'].set_visible(False)

    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)

    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()

    return image_base64