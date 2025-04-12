from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.views import View
from .forms import CustomLoginForm, JobSeekerRegistrationForm, EmployerRegistrationForm
from .models import JobSeeker, Employer

class LoginView(View):
    def get(self, request):
        form = CustomLoginForm()
        return render(request, 'users/login.html', {'form': form})
    
    def post(self, request):
        form = CustomLoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "You have been successfully logged in.")
                # Redirect based on user type
                if hasattr(user, 'jobseeker'):
                    return redirect('jobseeker_dashboard')
                elif hasattr(user, 'employer'):
                    return redirect('employer_dashboard')
                else:
                    return redirect('home')
            else:
                messages.error(request, "Invalid username or password.")
        return render(request, 'users/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, "You have been successfully logged out.")
    return redirect('login')

class JobSeekerRegistrationView(View):
    def get(self, request):
        form = JobSeekerRegistrationForm()
        return render(request, 'users/register_jobseeker.html', {'form': form})
    
    def post(self, request):
        form = JobSeekerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful. Welcome to eRecruitment!")
            return redirect('jobseeker_dashboard')
        return render(request, 'users/register_jobseeker.html', {'form': form})

class EmployerRegistrationView(View):
    def get(self, request):
        form = EmployerRegistrationForm()
        return render(request, 'users/register_employer.html', {'form': form})
    
    def post(self, request):
        form = EmployerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful. Welcome to eRecruitment!")
            return redirect('employer_dashboard')
        return render(request, 'users/register_employer.html', {'form': form})

class JobSeekerDashboardView(View):
    def get(self, request):
        if not request.user.is_authenticated or not hasattr(request.user, 'jobseeker'):
            messages.error(request, "You must be logged in as a job seeker to view this page.")
            return redirect('login')
        applications = request.user.jobseeker.applications.all()
        return render(request, 'users/jobseeker_dashboard.html', {'applications': applications})

class EmployerDashboardView(View):
    def get(self, request):
        if not request.user.is_authenticated or not hasattr(request.user, 'employer'):
            messages.error(request, "You must be logged in as an employer to view this page.")
            return redirect('login')
        jobs = request.user.employer.job_set.all()
        return render(request, 'users/employer_dashboard.html', {'jobs': jobs})
