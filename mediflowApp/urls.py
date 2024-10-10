from django.urls import path
from mediflowApp import views as mediflowViews

urlpatterns = [
    path('', mediflowViews.home, name="home"),
    path('new-exam/', mediflowViews.new_exam, name="new_exam"),
    path('new-patient/', mediflowViews.new_patient, name="new_patient"),
    path('exams/edit/<int:pk>/', mediflowViews.view_pdf, name="view_pdf"),
    path('exam/download/<int:path>', mediflowViews.download, name="download"),
    path('exam/next_exam/', mediflowViews.next_exam, name="next_exam"),
    path('patient-extraction/', mediflowViews.automated_patient_extraction, name="patient_extraction"),
    path('login/', mediflowViews.login_view, name='login'),
    path('logout/', mediflowViews.logout_view, name='logout'),
    path('exam/send_exam/<int:pk>', mediflowViews.email_view, name="send_exam"),
    path('search/', mediflowViews.search, name="search"),
]
