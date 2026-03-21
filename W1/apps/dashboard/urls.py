from django.urls import path
from .views import dashboard_home, doctor_dashboard, technician_dashboard

urlpatterns = [
    path('', dashboard_home, name='dashboard'),
    path('doctor-dashboard/', doctor_dashboard, name='doctor_dashboard'),
    path('technician-dashboard/', technician_dashboard, name='technician_dashboard'),
]