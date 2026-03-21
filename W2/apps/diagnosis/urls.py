from django.urls import path
from .views import run_diagnosis, view_result

urlpatterns = [
    path('run/<int:ecg_id>/', run_diagnosis, name='run_diagnosis'),
    path('result/<int:ecg_id>/', view_result, name='view_result'),
]