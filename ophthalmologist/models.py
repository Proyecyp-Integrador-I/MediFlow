from django.db import models

class Ophthalmologist(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    medical_license = models.CharField(max_length=50, unique=True)
    specialty = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name} {self.last_name}"

class Patient(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    identification = models.CharField(max_length=50, unique=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=10, blank=True, null=True) # CAMBIAR A LISTA DE TELEFONOS
    age = models.IntegerField(blank=True, null=True)
    date_of_birth = models.DateField(null=True)
    gender = models.CharField(max_length=50)
    address = models.CharField(max_length=100, blank=True, null=True)
    health_insurance = models.CharField(max_length=50)
    doctor = models.ForeignKey(Ophthalmologist, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.name} {self.last_name} {self.identification}"