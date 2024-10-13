from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_short_name(self):
        return self.first_name

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

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
    exam_date = models.DateField(null=True, blank=True)
    analysis_date = models.DateField(null=True, blank=True)
    file = models.FileField(upload_to='uploads/')
    result_analysis = models.TextField(blank=True)
    is_analyzed = models.BooleanField(default=False)
    apparatus = models.CharField(max_length=50, blank=True, null=True)
    exam_type = models.CharField(max_length=50, blank=True, null=True)

    #doctor = models.ForeignKey(Ophtalmologist, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)

    def __str__(self):
        return f"File {self.id} - {self.exam_date}"
