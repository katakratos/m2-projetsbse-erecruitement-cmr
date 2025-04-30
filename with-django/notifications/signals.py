from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from django.db.models import F
from applications.models import Application  # Import Application model
from .models import Notification

@receiver(post_save, sender=Application)
def create_notification_on_application_status_change(sender, instance, created, update_fields, **kwargs):
    """
    Create a notification when an application status changes to 'selected', 'rejected', or 'interview'
    """
    # Skip for new applications since there's no status change
    if created:
        return
        
    # Only create notifications for status changes - we'll check if 'status' was in update_fields
    # If update_fields is None, it means all fields might have been updated
    if update_fields is not None and 'status' not in update_fields:
        return
    
    if instance.status == 'selected':
        # Create a notification for the job seeker
        # JobSeeker is already a User, so we use jobseeker directly
        user = instance.jobseeker  # Fixed: JobSeeker is already a User subclass
        message = f"Congratulations! You have been selected for the position: {instance.job.title}"
        content_type = ContentType.objects.get_for_model(Application)
        
        Notification.objects.create(
            user=user,
            notification_type='application_status',
            message=message,
            content_type=content_type,
            object_id=instance.id
        )
    elif instance.status == 'rejected':
        # Create a rejection notification
        user = instance.jobseeker  # Fixed: JobSeeker is already a User subclass
        message = f"We regret to inform you that your application for {instance.job.title} was not selected."
        content_type = ContentType.objects.get_for_model(Application)
        
        Notification.objects.create(
            user=user,
            notification_type='application_status',
            message=message,
            content_type=content_type,
            object_id=instance.id
        )
    elif instance.status == 'interview':
        # Create an interview notification
        user = instance.jobseeker  # Fixed: JobSeeker is already a User subclass
        message = f"You have been selected for an interview for the position: {instance.job.title}."
        content_type = ContentType.objects.get_for_model(Application)
        
        Notification.objects.create(
            user=user,
            notification_type='application_status',
            message=message,
            content_type=content_type,
            object_id=instance.id
        )
