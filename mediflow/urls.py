"""
URL configuration for mediflow project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from mediflowApp import views as mediflowViews
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', mediflowViews.home, name="home"),
    path('new-exam/', mediflowViews.new_exam, name="new_exam"),
    path('new-patient/', mediflowViews.new_patient, name="new_patient"),
    path('exams/edit/<int:pk>/', mediflowViews.view_pdf, name="view_pdf"),
    path('exam/download/<int:path>', mediflowViews.download, name="download"),
    path('exam/next_exam/', mediflowViews.next_exam, name="next_exam"),
    path('patient-extraction/', mediflowViews.automated_patient_extraction, name="patient_extraction"),
    path('administrator/', mediflowViews.administrator, name="administrator"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)