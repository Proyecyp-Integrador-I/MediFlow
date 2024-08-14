from django.db import models

class Patient(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    phone = models.CharField(max_length=10) # CAMBIAR A LISTA DE TELEFONOS
    age = models.IntegerField()
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=50)
    address = models.CharField(max_length=100)
    health_insurance = models.CharField(max_length=50)



class Ophtalmologist(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    medical_license = models.CharField(max_length=50)
    title = models.CharField(max_length=50)
    address = models.CharField(max_length=100)

class Exam(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='uploads/')
    result_analysis = models.TextField(blank=True)
    is_analyzed = models.BooleanField(default=False)
    #apparatus = models.CharField(max_length=50)
    #exam_type = models.CharField(max_length=50)

    #doctor = models.ForeignKey(Ophtalmologist, on_delete=models.CASCADE)
    #patient = models.ForeignKey(Patient, on_delete=models.CASCADE)

    def __str__(self):
        return f"File {self.id} - {self.date}"
