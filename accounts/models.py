# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('supervisor', 'Supervisor'),
        ('intern', 'Intern'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='intern')
    phone = models.CharField(max_length=20, blank=True, null=True)
    
    def __str__(self):
        return self.username
    
    def is_admin(self):
        return self.role == 'admin'
    
    def is_supervisor(self):
        return self.role == 'supervisor'
    
    def is_intern(self):
        return self.role == 'intern'