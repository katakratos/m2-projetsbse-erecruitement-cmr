from celery import shared_task
from .utils.extraction import process_applications_for_job

@shared_task
def process_job_applications_task(job_id):
    """
    Celery task to process job applications asynchronously
    
    Args:
        job_id: The ID of the job to process applications for
        
    Returns:
        dict: Summary of the processing results
    """
    try:
        # Call the extraction function with the job_id
        results = process_applications_for_job(job_id)
        return results
    except Exception as e:
        # Return error information for debugging
        return {
            "error": str(e),
            "job_id": job_id,
            "processed": 0,
            "total": 0
        }
