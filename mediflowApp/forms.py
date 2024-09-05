from django import forms
from .models import Exam, Patient, Ophthalmologist

class UploadFileForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ['file']

    def __init__(self, *args, **kwargs):
        super(UploadFileForm, self).__init__(*args, **kwargs)
        self.fields['file'].widget.attrs.update({'accept': 'application/pdf'})  # Accept only PDFs

class UploadExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ['file', 'date', 'apparatus', 'exam_type', 'patient']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'})
        }

    def __init__(self, *args, **kwargs):
        super(UploadExamForm, self).__init__(*args, **kwargs)
        self.fields['file'].widget.attrs.update({'accept': 'application/pdf', 
            'multiple': True })  # Accept only PDFs

class AddPatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['identification', 'name', 'last_name', 'email', 'phone', 'date_of_birth', 'gender', 'address', 'health_insurance']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }
    def __init__(self, *args, **kwargs):
        super(AddPatientForm, self).__init__(*args, **kwargs)

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

class DeleteOphthalmologistForm(forms.ModelForm):
    class Meta:
        model = Ophthalmologist
        fields = ['medical_license']

class DeletePatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['identification']