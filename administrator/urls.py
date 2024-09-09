from django.urls import path
from administrator import views as adminViews

urlpatterns = [
    path('', adminViews.administrator, name="administrator"),
    path('new-ophthalmologist/', adminViews.new_ophthalmologist, name="new_ophthalmologist"),
    path('delete-ophthalmologist/<str:medical_license>/', adminViews.delete_ophthalmologist, name="delete_ophthalmologist"),
    path('delete-patient/<str:identification>/', adminViews.delete_patient, name="delete_patient"),
    path('edit-ophthalmologist/<str:medical_license>/', adminViews.edit_ophthalmologist, name="edit_ophthalmologist"),
    path('edit-patient/<str:identification>/', adminViews.edit_patient, name="edit_patient"),
    path('create-user/', adminViews.create_user, name='create_user'),
]
