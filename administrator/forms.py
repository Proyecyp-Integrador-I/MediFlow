from django import forms
from .models import *

class AddOphthalmologistForm(forms.ModelForm):
    class Meta:
        model = Ophthalmologist
        fields = ['id', 'name', 'last_name', 'email', 'medical_license', 'specialty']
    def __init__(self, *args, **kwargs):
        super(AddOphthalmologistForm, self).__init__(*args, **kwargs)

class EditOphthalmologistForm(forms.ModelForm):
    class Meta:
        model = Ophthalmologist
        fields = ['name', 'last_name', 'email', 'medical_license', 'specialty']

class EditPatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['identification', 'name', 'last_name', 'email', 'phone', 'date_of_birth', 'gender', 'address', 'health_insurance']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }