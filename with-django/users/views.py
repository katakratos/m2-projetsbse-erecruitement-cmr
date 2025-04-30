from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib import messages
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .forms import (
    CustomLoginForm, JobSeekerRegistrationForm, EmployerRegistrationForm,
    JobSeekerProfileUpdateForm, EmployerProfileUpdateForm, PasswordChangeCustomForm
)
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
                    # Changed 'home' to 'login' since there's no 'home' URL pattern
                    return redirect('login')
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

@method_decorator(login_required, name='dispatch')
class ProfileUpdateView(View):
    """View for users to update their profile information"""
    
    def get(self, request):
        user = request.user
        password_form = PasswordChangeCustomForm()
        
        if hasattr(user, 'jobseeker'):
            form = JobSeekerProfileUpdateForm(instance=user.jobseeker)
            template = 'users/profile_update.html'
            user_type = 'jobseeker'
        elif hasattr(user, 'employer'):
            form = EmployerProfileUpdateForm(instance=user.employer)
            template = 'users/profile_update.html'
            user_type = 'employer'
        else:
            messages.error(request, "User profile type not supported.")
            return redirect('login')
        
        context = {
            'form': form,
            'password_form': password_form,
            'user_type': user_type,
        }
        return render(request, template, context)
    
    def post(self, request):
        user = request.user
        update_type = request.POST.get('update_type')
        
        if update_type == 'profile':
            # Handle profile update
            if hasattr(user, 'jobseeker'):
                form = JobSeekerProfileUpdateForm(request.POST, instance=user.jobseeker)
                user_type = 'jobseeker'
                redirect_url = 'jobseeker_dashboard'
            elif hasattr(user, 'employer'):
                form = EmployerProfileUpdateForm(request.POST, instance=user.employer)
                user_type = 'employer'
                redirect_url = 'employer_dashboard'
            else:
                messages.error(request, "User profile type not supported.")
                return redirect('login')
            
            if form.is_valid():
                form.save()
                messages.success(request, "Your profile has been updated successfully!")
                return redirect(redirect_url)
            
            # If form is invalid, redisplay with errors
            password_form = PasswordChangeCustomForm()
            context = {
                'form': form,
                'password_form': password_form,
                'user_type': user_type,
            }
            return render(request, 'users/profile_update.html', context)
            
        elif update_type == 'password':
            # Handle password change
            form = PasswordChangeCustomForm(request.POST)
            
            if form.is_valid():
                # Check if current password is correct
                current_password = form.cleaned_data.get('current_password')
                if not user.check_password(current_password):
                    messages.error(request, "Your current password was entered incorrectly.")
                else:
                    # Check if new passwords match
                    new_password = form.cleaned_data.get('new_password')
                    confirm_password = form.cleaned_data.get('confirm_password')
                    
                    if new_password != confirm_password:
                        messages.error(request, "The new passwords do not match.")
                    else:
                        # Update password
                        user.set_password(new_password)
                        user.save()
                        # Update session to prevent logout
                        update_session_auth_hash(request, user)
                        messages.success(request, "Your password has been updated successfully!")
                        
                        if hasattr(user, 'jobseeker'):
                            return redirect('jobseeker_dashboard')
                        else:
                            return redirect('employer_dashboard')
            
            # If password form is invalid or validation failed, redisplay with errors
            if hasattr(user, 'jobseeker'):
                profile_form = JobSeekerProfileUpdateForm(instance=user.jobseeker)
                user_type = 'jobseeker'
            else:
                profile_form = EmployerProfileUpdateForm(instance=user.employer)
                user_type = 'employer'
            
            context = {
                'form': profile_form,
                'password_form': form,
                'user_type': user_type,
            }
            return render(request, 'users/profile_update.html', context)
        
        # If neither profile nor password update, redirect to profile update page
        messages.error(request, "Invalid form submission.")
        return redirect('profile_update')
