from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    return HttpResponse("<a href='new-exam/'>Agregar examen</a>")

def new_exam(request):
    return render(request, 'new_exam.html')