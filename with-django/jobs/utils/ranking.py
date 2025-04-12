import numpy as np
from django.db.models import F

def recalculate_ahp_ranks_for_job(job_id):
    """
    Recalculates candidate rankings based on AHP weights for a specific job.
    
    Args:
        job_id: The ID of the job to recalculate rankings for
        
    Returns:
        dict: Summary of ranking process
    """
    from jobs.models import Job, CandidateData
    
    try:
        job = Job.objects.get(id=job_id)
    except Job.DoesNotExist:
        return {"error": f"Job with ID {job_id} not found"}
    
    # Get all candidates for this job
    candidates = CandidateData.objects.filter(job_id=job_id)
    
    if not candidates.exists():
        return {"error": f"No candidates found for job {job_id}"}
    
    # Check if AHP priority weights exist
    try:
        ahp_priority = job.ahp_priority
        if not ahp_priority.weights or not ahp_priority.criteria_keys:
            return {"error": "AHP weights not set for this job"}
            
        weights = ahp_priority.weights
        criteria_keys = ahp_priority.criteria_keys
        
    except (Job.ahp_priority.RelatedObjectDoesNotExist, AttributeError):
        return {"error": "AHP priority matrix not found for this job"}
    
    # Map criteria keys to model field names
    criteria_to_field = {
        "bf": "business_unit_flexibility",
        "pe": "past_experience",
        "ed": "education_level", 
        "fl": "language_skills",
        "st": "strategic_thinking",
        "oc": "communication_skills",
        "cs": "computer_skills"
    }
    
    # Calculate weighted scores for all candidates
    candidate_scores = []
    
    for candidate in candidates:
        # Start with base score
        weighted_score = 0
        
        # Apply each weight to corresponding criterion
        for idx, key in enumerate(criteria_keys):
            weight = float(weights[idx])
            
            # Handle built-in criteria
            if key in criteria_to_field:
                field_name = criteria_to_field[key]
                criterion_value = getattr(candidate, field_name)
                weighted_score += weight * criterion_value
            
            # Handle custom criteria (those starting with 'c')
            elif key.startswith('c'):
                try:
                    # Extract ID from key (format: 'c123' where 123 is the ID)
                    criteria_id = int(key[1:])
                    custom_scores = candidate.custom_criteria_scores or {}
                    
                    # Use the ID as a string key in the custom_criteria_scores JSON
                    if str(criteria_id) in custom_scores:
                        criterion_value = float(custom_scores[str(criteria_id)])
                        weighted_score += weight * criterion_value
                except (ValueError, TypeError):
                    pass
        
        candidate_scores.append((candidate.id, weighted_score))
    
    # Sort candidates by their weighted scores (descending)
    candidate_scores.sort(key=lambda x: x[1], reverse=True)
    
    # Update ranks
    for rank, (candidate_id, score) in enumerate(candidate_scores, 1):
        CandidateData.objects.filter(id=candidate_id).update(
            ahp_rank=rank,
            # Store the weighted score as well
            final_score=score
        )
    
    return {
        "job_id": job_id,
        "candidates_ranked": len(candidate_scores),
        "status": "success"
    }
