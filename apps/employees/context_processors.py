def notification_count(request):
    """Add unread notification count to all employee templates."""
    if request.user.is_authenticated and hasattr(request.user, 'employee_profile'):
        try:
            count = request.user.employee_profile.notifications.filter(is_read=False).count()
            return {'unread_notification_count': count}
        except:
            pass
    return {'unread_notification_count': 0}