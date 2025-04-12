from django.urls import path
from . import views

urlpatterns = [
    # Fix URL pattern name to match what's used in the template
    path('job/<int:job_id>/apply/', views.ApplyForJobView.as_view(), name='apply_for_job'),
    path('job/<int:job_id>/applications/', views.EmployerApplicationsView.as_view(), name='employer_applications'),
]
