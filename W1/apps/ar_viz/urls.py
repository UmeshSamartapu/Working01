from django.urls import path
from .views import ar_view

urlpatterns = [
    path('', ar_view, name='ar_view'),
]