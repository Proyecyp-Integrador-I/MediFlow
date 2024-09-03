from django.contrib import admin
from .models import Exam, Patient, Ophthalmologist


admin.site.register(Exam)
admin.site.register(Patient)
admin.site.register(Ophthalmologist)