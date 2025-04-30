from django import template
from jobs.models import CandidateData

register = template.Library()

@register.filter
def get_jobseeker_name(jobseeker_id):
    """
    Get the extracted name from CandidateData for a jobseeker.
    This fetches the name from the CV extraction, not the account name.
    """
    try:
        # Get the most recent CandidateData entry for this jobseeker
        candidate_data = CandidateData.objects.filter(jobseeker_id=jobseeker_id).first()
        if candidate_data and candidate_data.name:
            return candidate_data.name
        return f"Applicant #{jobseeker_id}"
    except Exception:
        return f"Applicant #{jobseeker_id}"
