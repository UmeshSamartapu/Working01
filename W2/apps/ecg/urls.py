from django.urls import path
from .views import upload_ecg, ecg_list

urlpatterns = [
    path('upload/', upload_ecg, name='upload_ecg'),
    path('', ecg_list, name='ecg_list'),   # ✅ THIS LINE FIXES /ecg/
]