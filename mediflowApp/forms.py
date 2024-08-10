from django import forms
from .models import Exam

class UploadFileForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ['file']

    def __init__(self, *args, **kwargs):
        super(UploadFileForm, self).__init__(*args, **kwargs)
        self.fields['file'].widget.attrs.update({'accept': 'application/pdf'})  # Aceptar solo PDFs