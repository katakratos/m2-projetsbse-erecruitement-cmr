from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/jobseeker/', views.JobSeekerRegistrationView.as_view(), name='register_jobseeker'),
    path('register/employer/', views.EmployerRegistrationView.as_view(), name='register_employer'),
    path('dashboard/jobseeker/', views.JobSeekerDashboardView.as_view(), name='jobseeker_dashboard'),
    path('dashboard/employer/', views.EmployerDashboardView.as_view(), name='employer_dashboard'),
]
