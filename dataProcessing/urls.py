from django.urls import path
from .views import ocr_view

app = "dataProcessing"

urlpatterns = [
    path('ocr/<int:id>', ocr_view, name="ocr"),
]
