from django import forms
from .models import Exam

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
        fields = ['file', 'exam_date', 'apparatus', 'exam_type', 'patient']
        widgets = {
            'exam_date': forms.DateInput(attrs={'type': 'date'})
        }

    def __init__(self, *args, **kwargs):
        super(UploadExamForm, self).__init__(*args, **kwargs)
        self.fields['file'].widget.attrs.update({'accept': 'application/pdf', 
            'multiple': True })  # Accept only PDFs