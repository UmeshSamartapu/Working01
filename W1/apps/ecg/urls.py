from django.urls import path
from .views import upload_ecg

urlpatterns = [
    path('upload/', upload_ecg, name='upload_ecg'),
]