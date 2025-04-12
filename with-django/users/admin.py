from django.contrib import admin
from .models import User, JobSeeker, Employer
from django.contrib.auth.admin import UserAdmin

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('phone_number',)}),
    )

@admin.register(JobSeeker)
class JobSeekerAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name')
    
    def get_queryset(self, request):
        return super().get_queryset(request).filter(jobseeker__isnull=False)

@admin.register(Employer)
class EmployerAdmin(UserAdmin):
    list_display = ('username', 'email', 'company_name')
    fieldsets = UserAdmin.fieldsets + (
        ('Company Info', {'fields': ('company_name', 'company_description')}),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).filter(employer__isnull=False)
