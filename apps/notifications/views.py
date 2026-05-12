from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Notification

@login_required
def mark_read(request, notif_id):
    notif = get_object_or_404(Notification, id=notif_id, user=request.user)
    notif.is_read = True
    notif.save()
    return redirect(request.META.get('HTTP_REFERER', 'core:dashboard'))

@login_required
def mark_all_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return redirect(request.META.get('HTTP_REFERER', 'core:dashboard'))
