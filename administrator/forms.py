from django import forms
from .models import *
from .models import CustomUser
from ophthalmologist.models import Ophthalmologist, Patient

class CustomUserCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

class AddOphthalmologistForm(forms.ModelForm):
    class Meta:
        model = Ophthalmologist
        fields = ['id', 'name', 'last_name', 'email', 'medical_license', 'specialty']

    def save(self, commit=True):
        # Crear el objeto Ophthalmologist
        ophthalmologist = super().save(commit=False)
        
        if commit:
            ophthalmologist.save()  # Guardar el oftalmólogo en la BD

            # Crear el usuario asociado al oftalmólogo
            user = CustomUser(
                email=ophthalmologist.email,
                first_name=ophthalmologist.name,
                last_name=ophthalmologist.last_name,
                ophthalmologist=ophthalmologist
            )
            
            # Generar la contraseña (por ejemplo, basada en nombre y apellido)
            raw_password = f"{ophthalmologist.name}{ophthalmologist.last_name}".lower()
            
            # Guardar la contraseña de manera segura
            user.set_password(raw_password)
            user.save()

        return ophthalmologist

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