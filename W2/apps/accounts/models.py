from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('doctor', 'Doctor'),
        ('technician', 'Technician'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='doctor')

    def __str__(self):
        return self.username