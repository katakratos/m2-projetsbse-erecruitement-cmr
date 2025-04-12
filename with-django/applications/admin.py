from django.contrib import admin
from .models import Application

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('jobseeker', 'job', 'status', 'date_applied')
    list_filter = ('status', 'date_applied', 'job')
    search_fields = ('job__title', 'jobseeker__username', 'jobseeker__first_name', 'jobseeker__last_name')
    date_hierarchy = 'date_applied'
    
    fieldsets = (
        ('Application Info', {
            'fields': ('jobseeker', 'job', 'status',)
        }),
        ('Documents', {
            'fields': ('cv',)
        }),
    )
