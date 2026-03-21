from django.urls import path
from .views import *

urlpatterns = [
    path('', patient_list, name='patient_list'),
    path('add/', add_patient, name='add_patient'),
    path('edit/<int:id>/', edit_patient, name='edit_patient'),
    path('delete/<int:id>/', delete_patient, name='delete_patient'),
]