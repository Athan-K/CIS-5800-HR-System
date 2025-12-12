from apps.employees.models import LeaveRequest, AttendanceCorrection


def pending_counts(request):
    """Add pending counts to all HR templates."""
    if request.user.is_authenticated and hasattr(request.user, 'is_hr') and request.user.is_hr:
        return {
            'pending_leave_count': LeaveRequest.objects.filter(status='pending').count(),
            'pending_correction_count': AttendanceCorrection.objects.filter(status='pending').count(),
        }
    return {}