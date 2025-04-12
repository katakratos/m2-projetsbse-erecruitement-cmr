from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    def __str__(self):
        return self.username
        
    class Meta:
        pass

class JobSeeker(User):
    
    def __str__(self):
        return f"{self.username} - Job Seeker"

class Employer(User):
    company_name = models.CharField(max_length=100, blank=True)
    company_description = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.username} - Employer"