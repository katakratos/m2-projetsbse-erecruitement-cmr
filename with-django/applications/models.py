from django.db import models
from users.models import JobSeeker
from jobs.models import Job

def cv_upload_path(instance, filename):
    """Function to determine the upload path for CV files"""
    # Store CV in 'data/user_id/filename'
    # JobSeeker IS a User (inherits from User), not HAS a User
    return f'data/{instance.jobseeker.id}/{filename}'

class Application(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    jobseeker = models.ForeignKey(JobSeeker, on_delete=models.CASCADE, related_name='applications')
    cv = models.FileField(upload_to=cv_upload_path)
    date_applied = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default='pending')
    
    def __str__(self):
        return f"{self.jobseeker.get_full_name()} - {self.job.title}"
    
    class Meta:
        unique_together = ('job', 'jobseeker')  # Prevent duplicate applications