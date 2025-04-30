import django_filters
from django import forms
from django.db.models import Q  # Add this import for Q objects
from .models import Job

class JobFilter(django_filters.FilterSet):
    """
    Filter for Job model that handles all the filtering logic
    for the job list page.
    """
    # Text search across title and description
    q = django_filters.CharFilter(method='filter_search', label="Search")
    
    # Location filter with autocomplete
    location = django_filters.CharFilter(
        field_name='location', 
        lookup_expr='icontains', 
        label="Location"
    )
    
    # Job type filter (multiple choice)
    type = django_filters.MultipleChoiceFilter(
        choices=Job.JOB_TYPE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        label="Job Type"
    )
    
    # Experience level filter (multiple choice)  
    experience = django_filters.MultipleChoiceFilter(
        choices=Job.EXPERIENCE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        label="Experience Level"
    )
    
    # Salary range filter (range)
    min_salary = django_filters.NumberFilter(
        field_name='salary', 
        lookup_expr='gte', 
        label="Min Salary (XAF)"
    )
    max_salary = django_filters.NumberFilter(
        field_name='salary', 
        lookup_expr='lte', 
        label="Max Salary (XAF)"
    )
    
    # Experience years required filter
    years_experience_required = django_filters.NumberFilter(
        field_name='years_experience_required', 
        lookup_expr='lte', 
        label="Max Years Required"
    )
    
    # Remote work filter (boolean)
    remote = django_filters.BooleanFilter(
        field_name='remote_work', 
        label="Remote Work Available"
    )
    
    # Sorting options
    SORT_OPTIONS = (
        ('created_at', 'Most recent'),
        ('title', 'Most relevant'),
        ('salary', 'Highest salary'),
        ('-salary', 'Lowest salary'),
    )
    
    sort = django_filters.ChoiceFilter(
        choices=SORT_OPTIONS,
        method='filter_sort',
        label="Sort by"
    )
    
    def filter_search(self, queryset, name, value):
        """Filter by searching title and description"""
        if not value:
            return queryset
        
        return queryset.filter(
            Q(title__icontains=value) | 
            Q(description__icontains=value)
        )
    
    def filter_sort(self, queryset, name, value):
        """Sort queryset based on selection"""
        if value:
            return queryset.order_by(value)
        # Default to most recent
        return queryset.order_by('-created_at')

    class Meta:
        model = Job
        fields = [
            'q', 'location', 'type', 'experience', 
            'min_salary', 'max_salary', 'years_experience_required',
            'remote', 'sort'
        ]
