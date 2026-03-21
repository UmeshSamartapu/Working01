from django.urls import path
from .views import result_view

urlpatterns = [
    path('', result_view, name='results'),
]