from django.shortcuts import render
from ophthalmologist.models import Patient
from exam.models import Exam
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import date, timedelta
from django.db.models import Count
from io import BytesIO
import base64

def visualizeStatistics(request):
    try:
        graphAges = patientByAge()
        graphExamsByDate = examsByDate()
        graphGender = patientByGender()
        graphInsurance = patientByInsurance()
        return render(request, 'statistics.html', {'graphAges': graphAges, 'graphGender': graphGender, 'graphInsurance': graphInsurance, 'graphToday': graphExamsByDate['graphToday'], 
        'graphLastSevenDays': graphExamsByDate['graphLastSevenDays'], 'graphLastMonth': graphExamsByDate['graphLastMonth'], 'graphThisYear': graphExamsByDate['graphThisYear'], 
        'graphAllYears': graphExamsByDate['graphAllYears']})
    except:
        return render(request, 'statistics-error.html')

def createStatistics(x_param, y_param, x_label, y_label, graph_type):
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Helvetica', 'Arial']
    plt.figure(figsize=(10, 6))
    if graph_type == 'bar':
        plt.bar(x_param, y_param, color='#262d40')
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.xticks()
        plt.ylim(0, None)
        plt.yticks(range(0, max(y_param) + 1))
        ax = plt.gca()
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
    elif graph_type == 'pie':
        wedges, texts, autotexts = plt.pie(y_param, autopct='%1.1f%%', colors=['#262d40', '#6A80C1'], startangle=90)
        plt.axis('equal')
        plt.legend(wedges, x_param, title="Genders", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1), fontsize=10, title_fontsize='13')
        
    

    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)

    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()

    return image_base64

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

    graphAges = createStatistics(age_labels, age_counts, 'Age Range', 'Number of Patients', 'bar')

    return graphAges

def patientByGender():
    male_count = Patient.objects.filter(gender='M').count()
    male_count += Patient.objects.filter(gender='Male').count()
    female_count = Patient.objects.filter(gender='F').count()
    female_count += Patient.objects.filter(gender='Female').count()

    genders = ['Male', 'Female']
    counts = [male_count, female_count]

    graphGender = createStatistics(genders, counts, 'Gender', 'Number of Patients', 'pie')

    return graphGender

def patientByInsurance():
    insurance_counts = Patient.objects.values('health_insurance').annotate(count=Count('id')).order_by('health_insurance')

    insurance_types = [entry['health_insurance'] for entry in insurance_counts]
    counts = [entry['count'] for entry in insurance_counts]

    graphInsurance = createStatistics(insurance_types, counts, 'Health Insurance', 'Number of Patients', 'bar')

    return graphInsurance

def examsByDate():
    today = date.today()

    dates, counts = examsByDateFilter(today, 'today')
    graphToday = createStatistics(dates, counts, 'Today', 'Number of Exams Analyzed', 'bar')
    dates, counts = examsByDateFilter(today - timedelta(days=6), 'last_7_days')
    graphLastSevenDays = createStatistics(dates, counts, 'Last Seven Days', 'Number of Exams Analyzed', 'bar')
    dates, counts = examsByDateFilter(today - timedelta(days=29), 'last_month')
    graphLastMonth = createStatistics(dates, counts, 'Last Month', 'Number of Exams Analyzed', 'bar')
    dates, counts = examsByDateFilter(today - timedelta(days=364), 'this_year')
    graphThisYear = createStatistics(dates, counts, 'This Year', 'Number of Exams Analyzed', 'bar')
    dates, counts = examsByDateFilter(Exam.objects.earliest('analysis_date').analysis_date, 'all_years')
    graphAllYears = createStatistics(dates, counts, 'All Years', 'Number of Exams Analyzed','bar')


    graphExamsByDate = {
        'graphToday': graphToday,
        'graphLastSevenDays': graphLastSevenDays,
        'graphLastMonth': graphLastMonth,
        'graphThisYear': graphThisYear,
        'graphAllYears': graphAllYears
    }

    return graphExamsByDate

def examsByDateFilter(start_date, filter_option):
    end_date = date.today()

    exams_per_day = (
        Exam.objects.filter(analysis_date__range=[start_date, end_date])
        .values('analysis_date')
        .annotate(count=Count('id'))
        .order_by('analysis_date')
    )

    date_range = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]
    dates = [d.strftime('%d-%m-%Y') for d in date_range]
    counts = [0] * len(dates)

    for exam in exams_per_day:
        exam_date_str = exam['analysis_date'].strftime('%d-%m-%Y')
        if exam_date_str in dates:
            index = dates.index(exam_date_str)
            counts[index] = exam['count']

    if filter_option == 'last_month':
        days = [d.day for d in date_range]
        dates = [str(day) for day in days]

    elif filter_option == 'this_year':
        month_labels = []
        month_counts = [0] * 12

        for exam in exams_per_day:
            exam_date = exam['analysis_date']
            month_index = exam_date.month - 1
            month_counts[month_index] += exam['count']

        month_short_names = ["Jan.", "Feb.", "Mar.", "Apr.", "May", "Jun.", "Jul.", "Aug.", "Sep.", "Oct.", "Nov.", "Dec."]
        for month in range(1, 13):
            month_labels.append(month_short_names[month - 1])

        dates = month_labels
        counts = month_counts

    elif filter_option == 'all_years':
        year_labels = sorted(set(d.year for d in date_range))
        counts_by_year = []
        
        for year in year_labels:
            year_count = sum(counts[i] for i in range(len(date_range)) if date_range[i].year == year)
            counts_by_year.append(year_count)

        dates = [str(year) for year in year_labels]
        counts = counts_by_year

    else:
        dates = [d.strftime('%d-%m-%Y') for d in date_range]
    
    return dates, counts