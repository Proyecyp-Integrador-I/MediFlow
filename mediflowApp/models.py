from django.db import models

class Patient(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    identification = models.CharField(max_length=50)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=10, blank=True, null=True) # CAMBIAR A LISTA DE TELEFONOS
    age = models.IntegerField(blank=True, null=True)
    date_of_birth = models.DateField(null=True)
    gender = models.CharField(max_length=50)
    address = models.CharField(max_length=100, blank=True, null=True)
    health_insurance = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name} {self.last_name} {self.identification}"

class Ophthalmologist(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    medical_license = models.CharField(max_length=50)
    specialty = models.CharField(max_length=50)

class Exam(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.DateField(null=True, blank=True)
    file = models.FileField(upload_to='uploads/')
    result_analysis = models.TextField(blank=True)
    is_analyzed = models.BooleanField(default=False)
    apparatus = models.CharField(max_length=50, blank=True, null=True)
    exam_type = models.CharField(max_length=50, blank=True, null=True)

    #doctor = models.ForeignKey(Ophtalmologist, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)

    def __str__(self):
        return f"File {self.id} - {self.date}"
