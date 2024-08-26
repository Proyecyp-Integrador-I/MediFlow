from django.contrib import admin
from .models import Exam, Patient, Ophtalmologist


admin.site.register(Exam)
admin.site.register(Patient)
admin.site.register(Ophtalmologist)