from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views import View
from django.utils.decorators import method_decorator
from .models import Application
from .forms import ApplicationForm
from jobs.models import Job

@method_decorator(login_required, name='dispatch')
class ApplyForJobView(View):
    def get(self, request, job_id):
        job = get_object_or_404(Job, id=job_id)
        
        # Check if user is a job seeker
        if not hasattr(request.user, 'jobseeker'):
            messages.error(request, "Only job seekers can apply for jobs.")
            return redirect('job_detail', job_id=job_id)
        
        # Check if already applied
        if Application.objects.filter(job=job, jobseeker=request.user.jobseeker).exists():
            messages.warning(request, "You have already applied for this job.")
            return redirect('job_detail', job_id=job_id)
        
        form = ApplicationForm()
        return render(request, 'applications/apply.html', {'form': form, 'job': job})
    
    def post(self, request, job_id):
        job = get_object_or_404(Job, id=job_id)
        
        # Check if user is a job seeker
        if not hasattr(request.user, 'jobseeker'):
            messages.error(request, "Only job seekers can apply for jobs.")
            return redirect('job_detail', job_id=job_id)
        
        # Check if already applied
        if Application.objects.filter(job=job, jobseeker=request.user.jobseeker).exists():
            messages.warning(request, "You have already applied for this job.")
            return redirect('job_detail', job_id=job_id)
        
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.jobseeker = request.user.jobseeker
            application.save()
            messages.success(request, "Your application has been submitted successfully.")
            return redirect('jobseeker_dashboard')
        
        return render(request, 'applications/apply.html', {'form': form, 'job': job})

@method_decorator(login_required, name='dispatch')
class EmployerApplicationsView(View):
    def get(self, request, job_id):
        job = get_object_or_404(Job, id=job_id)
        
        # Check if user is the employer for this job
        if not hasattr(request.user, 'employer') or request.user.employer != job.employer:
            messages.error(request, "You don't have permission to view applications for this job.")
            return redirect('employer_dashboard')
        
        applications = job.applications.all()
        return render(request, 'applications/employer_applications.html', {
            'applications': applications,
            'job': job
        })