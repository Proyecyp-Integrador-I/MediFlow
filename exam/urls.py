from django.urls import path
from exam import views as examViews

urlpatterns = [
    path('new-exam/', examViews.new_exam, name="new_exam"),
    path('download/<int:path>', examViews.download, name="download"),
    path('send-exam/<int:pk>', examViews.email_view, name="send_exam"),
]
