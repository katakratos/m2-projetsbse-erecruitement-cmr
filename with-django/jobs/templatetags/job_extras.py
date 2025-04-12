from django import template
from applications.models import Application

register = template.Library()

@register.filter
def has_applied(job, jobseeker):
    """Check if a job seeker has applied for a specific job"""
    return Application.objects.filter(job=job, jobseeker=jobseeker).exists()

@register.filter
def get_field_by_name(fields_dict, name):
    """Get a form field by name"""
    for field_name, field in fields_dict.items():
        if field_name == name:
            return field
    return None
