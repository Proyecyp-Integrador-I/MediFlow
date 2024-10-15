from django.urls import path
from ophthalmologist import views as ophthalmologistViews

urlpatterns = [
    path('', ophthalmologistViews.home, name="home"),
    path('new-patient/', ophthalmologistViews.new_patient, name="new_patient"),
    path('edit/<int:pk>/', ophthalmologistViews.view_pdf, name="view_pdf"),
    path('next_exam/', ophthalmologistViews.next_exam, name="next_exam"),
    path('patient-extraction/', ophthalmologistViews.automated_patient_extraction, name="patient_extraction"),
    path('login/', ophthalmologistViews.login_view, name='login'),
    path('logout/', ophthalmologistViews.logout_view, name='logout'),
    path('search/', ophthalmologistViews.search, name="search"),
]
