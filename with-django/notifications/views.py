from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib import messages
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Notification

class NotificationListView(LoginRequiredMixin, View):
    """View to display all notifications for a user"""
    def get(self, request):
        notifications = Notification.objects.filter(user=request.user)
        unread_count = notifications.filter(is_read=False).count()
        
        return render(request, 'notifications/notification_list.html', {
            'notifications': notifications,
            'unread_count': unread_count
        })

class MarkNotificationReadView(LoginRequiredMixin, View):
    """View to mark a notification as read"""
    def post(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk, user=request.user)
        notification.is_read = True
        notification.save()
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        
        messages.success(request, "Notification marked as read.")
        return redirect('notifications:list')

class MarkAllNotificationsReadView(LoginRequiredMixin, View):
    """View to mark all notifications as read"""
    def post(self, request):
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        
        messages.success(request, "All notifications marked as read.")
        return redirect('notifications:list')

class DeleteNotificationView(LoginRequiredMixin, View):
    """View to delete a notification"""
    def post(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk, user=request.user)
        notification.delete()
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        
        messages.success(request, "Notification deleted.")
        return redirect('notifications:list')

@login_required
def notifications_view(request):
    # Replace this with your actual notification logic
    notifications = []
    return render(request, 'notifications/notifications.html', {'notifications': notifications})
