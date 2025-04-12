from django.db import models
from users.models import Employer, JobSeeker
# Create your models here.


class Job(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    employer = models.ForeignKey(Employer, on_delete=models.CASCADE)
    nb_places = models.IntegerField(default=1)
    location = models.CharField(max_length=255)
    type = models.CharField(max_length=50)
    experience = models.CharField(max_length=50)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    deadline = models.DateField()
    requirements = models.TextField()
    skills = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Basic criteria fields (these could be implemented as boolean fields for quick filtering)
    business_unit_flexibility = models.BooleanField(default=False, help_text="Ability to work in different business units")
    past_experience_required = models.BooleanField(default=False)
    min_education_level = models.CharField(max_length=100, blank=True, null=True)
    foreign_language_required = models.BooleanField(default=False)
    strategic_thinking_required = models.BooleanField(default=False)
    oral_communication_required = models.BooleanField(default=False)
    computer_skills_required = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title
    
class Criteria(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    criteria = models.CharField(max_length=255)
    
    def __str__(self):
        return f"Criteria for {self.job.title}"
    
class Candidates(models.Model):
    "This model represent the candidates selected for a job"
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    user = models.ForeignKey(JobSeeker, on_delete=models.CASCADE)
    ahp_rank = models.FloatField()
    final_score = models.FloatField()
    
    def __str__(self):
        return f"{self.user.username} - {self.job.title}"

class AHPPriority(models.Model):
    job = models.OneToOneField(Job, on_delete=models.CASCADE, related_name='ahp_priority')
    matrix_data = models.JSONField(help_text="The pairwise comparison matrix")
    criteria_keys = models.JSONField(help_text="List of criteria keys used in the matrix")
    criteria_names = models.JSONField(help_text="List of criteria names shown to user")
    weights = models.JSONField(help_text="The calculated priority weights for each criterion")
    consistency_ratio = models.FloatField(help_text="Consistency ratio of the matrix")
    is_consistent = models.BooleanField(default=False, help_text="Whether the matrix is consistent (CR < 0.1)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"AHP Priority for {self.job.title} (CR: {self.consistency_ratio:.4f})"
    
class CandidateData(models.Model):
    """Model to store extracted candidate data from CV analysis"""
    application = models.OneToOneField('applications.Application', on_delete=models.CASCADE, related_name='candidate_data')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='candidate_data')
    jobseeker = models.ForeignKey(JobSeeker, on_delete=models.CASCADE, related_name='candidate_data')
    raw_data = models.JSONField(help_text="Raw extracted data from the CV")
    
    # Core details 
    name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    years_experience = models.CharField(max_length=100, blank=True, null=True)
    
    # Evaluation scores (0-100)
    business_unit_flexibility = models.FloatField(default=0)
    past_experience = models.FloatField(default=0)
    education_level = models.FloatField(default=0)
    language_skills = models.FloatField(default=0)
    strategic_thinking = models.FloatField(default=0)
    communication_skills = models.FloatField(default=0)
    computer_skills = models.FloatField(default=0)
    
    # Custom criteria scores (stored as JSON)
    custom_criteria_scores = models.JSONField(default=dict, blank=True)
    
    # Overall score
    final_score = models.FloatField(default=0)
    ahp_rank = models.IntegerField(default=0)
    
    # Selection status
    is_selected = models.BooleanField(default=False, help_text="Indicates if the candidate has been selected for the position")
    selection_date = models.DateTimeField(null=True, blank=True, help_text="When the candidate was selected")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Data for {self.jobseeker.get_full_name()} - {self.job.title}"
    
    class Meta:
        ordering = ['-final_score']