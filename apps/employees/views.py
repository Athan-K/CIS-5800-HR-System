"""
Employee self-service views.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from apps.core.mixins import EmployeeRequiredMixin
from django.views.generic import TemplateView, UpdateView
from .models import Employee, Attendance, Payslip, LeaveRequest, AttendanceCorrection, Notification
from .forms import LeaveRequestForm, ProfileUpdateForm
from datetime import datetime, timedelta




class EmployeeDashboardView(EmployeeRequiredMixin, TemplateView):
    """Employee dashboard showing overview of their information."""
    template_name = 'employees/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        employee = self.request.user.employee_profile
        
        # Get current month's attendance
        from datetime import date
        import calendar
        
        today = date.today()
        first_day = today.replace(day=1)
        last_day = today.replace(day=calendar.monthrange(today.year, today.month)[1])
        
        # Get attendance records for current month
        monthly_attendance = employee.attendance_records.filter(
            date__gte=first_day,
            date__lte=last_day
        ).order_by('date')
        
        # Create calendar data
        cal = calendar.Calendar(firstweekday=6)  # Start on Sunday
        month_days = cal.monthdayscalendar(today.year, today.month)
        
        # Build attendance lookup
        attendance_dict = {a.date.day: a for a in monthly_attendance}
        
        # Calculate monthly stats
        present_count = monthly_attendance.filter(status='present').count()
        late_count = monthly_attendance.filter(status='late').count()
        absent_count = monthly_attendance.filter(status='absent').count()
        leave_count = monthly_attendance.filter(status='on_leave').count()
        
        # Get last recorded attendance
        last_attendance = employee.attendance_records.order_by('-date').first()
        
        context['employee'] = employee
        context['recent_attendance'] = employee.attendance_records.all()[:5]
        context['latest_payslip'] = employee.payslips.first()
        context['pending_requests'] = employee.leave_requests.filter(
            status=LeaveRequest.Status.PENDING
        ).count()
        context['leave_balances'] = {
            'annual': employee.annual_leave_balance,
            'vacation': employee.vacation_balance,
            'sick': employee.sick_leave_balance,
        }
        
        # Calendar data
        context['calendar_weeks'] = month_days
        context['attendance_dict'] = attendance_dict
        context['current_month'] = today.strftime('%B %Y')
        context['today'] = today.day
        
        # Monthly stats
        context['monthly_stats'] = {
            'present': present_count,
            'late': late_count,
            'absent': absent_count,
            'on_leave': leave_count,
            'total_days': present_count + late_count + absent_count + leave_count,
        }
        context['last_attendance'] = last_attendance
        
        return context


@login_required
def profile_view(request):
    """View and update employee profile."""
    employee = get_object_or_404(Employee, user=request.user)
    
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('employees:profile')
    else:
        form = ProfileUpdateForm(instance=employee)
    
    return render(request, 'employees/profile.html', {
        'employee': employee,
        'form': form,
    })


@login_required
def attendance_view(request):
    """View attendance records for the logged-in employee."""
    employee = get_object_or_404(Employee, user=request.user)
    
    # Get date filters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    attendance_records = employee.attendance_records.all().order_by('-date')
    
    if start_date:
        attendance_records = attendance_records.filter(date__gte=start_date)
    if end_date:
        attendance_records = attendance_records.filter(date__lte=end_date)
    
    # Get pending corrections for this employee
    pending_corrections = employee.attendance_corrections.filter(
        status=AttendanceCorrection.Status.PENDING
    )
    
    # Get recent corrections (approved/rejected)
    recent_corrections = employee.attendance_corrections.exclude(
        status=AttendanceCorrection.Status.PENDING
    ).order_by('-reviewed_at')[:5]
    
    # Create a dict of dates with pending corrections
    pending_correction_dates = {c.date: c for c in pending_corrections}
    
    context = {
        'employee': employee,
        'attendance_records': attendance_records[:30],  # Last 30 records
        'pending_corrections': pending_corrections,
        'recent_corrections': recent_corrections,
        'pending_correction_dates': pending_correction_dates,
    }
    return render(request, 'employees/attendance.html', context)


@login_required
def payslips_view(request):
    """View payslips."""
    employee = get_object_or_404(Employee, user=request.user)
    payslips = employee.payslips.all()
    
    return render(request, 'employees/payslips.html', {
        'employee': employee,
        'payslips': payslips,
    })


@login_required
def leave_request_view(request):
    """View and submit leave requests."""
    employee = get_object_or_404(Employee, user=request.user)
    
    if request.method == 'POST':
        leave_type = request.POST.get('leave_type')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        reason = request.POST.get('reason', '')
        
        from datetime import datetime
        start = datetime.strptime(start_date, '%Y-%m-%d').date()
        end = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        # Calculate business days for validation
        days = 0
        current = start
        while current <= end:
            if current.weekday() < 5:  # Monday = 0, Sunday = 6
                days += 1
            current += timedelta(days=1)
        
        # Check balance for paid leave types
        if leave_type == 'annual' and days > employee.annual_leave_balance:
            messages.error(request, 'Insufficient annual leave balance.')
            return redirect('employees:leave_request')
        elif leave_type == 'vacation' and days > employee.vacation_balance:
            messages.error(request, 'Insufficient vacation balance.')
            return redirect('employees:leave_request')
        elif leave_type == 'sick' and days > employee.sick_leave_balance:
            messages.error(request, 'Insufficient sick leave balance.')
            return redirect('employees:leave_request')
        
        # Create leave request without days_requested (it's a computed property)
        LeaveRequest.objects.create(
            employee=employee,
            leave_type=leave_type,
            start_date=start,
            end_date=end,
            reason=reason,
        )
        
        messages.success(request, f'Leave request submitted successfully! ({days} day{"s" if days != 1 else ""})')
        return redirect('employees:leave_request')
    
    # Get pending requests
    pending_requests = employee.leave_requests.filter(
        status=LeaveRequest.Status.PENDING
    ).order_by('-submitted_at')
    
    # Get recent requests (last 10)
    recent_requests = employee.leave_requests.all().order_by('-submitted_at')[:10]
    
    context = {
        'employee': employee,
        'leave_balances': {
            'annual': employee.annual_leave_balance,
            'vacation': employee.vacation_balance,
            'sick': employee.sick_leave_balance,
        },
        'pending_requests': pending_requests,
        'recent_requests': recent_requests,
    }
    return render(request, 'employees/leave_request.html', context)


@login_required
def check_leave_balance(request):
    """HTMX endpoint to check leave balance."""
    employee = get_object_or_404(Employee, user=request.user)
    leave_type = request.GET.get('leave_type')
    
    balances = {
        'annual': employee.annual_leave_balance,
        'vacation': employee.vacation_balance,
        'sick': employee.sick_leave_balance,
    }
    
    balance = balances.get(leave_type, 0)
    
    return JsonResponse({'balance': float(balance)})


class EmployeeSettingsView(EmployeeRequiredMixin, TemplateView):
    """Employee Settings page."""
    template_name = 'employees/settings.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        context['employee'] = self.request.user.employee_profile
        return context
    

@login_required
def attendance_calendar(request):
    """HTMX endpoint for interactive attendance calendar."""
    from datetime import date
    import calendar
    
    employee = get_object_or_404(Employee, user=request.user)
    
    # Get month/year from request, default to current month
    year = int(request.GET.get('year', date.today().year))
    month = int(request.GET.get('month', date.today().month))
    
    # Handle month overflow
    if month > 12:
        month = 1
        year += 1
    elif month < 1:
        month = 12
        year -= 1
    
    first_day = date(year, month, 1)
    last_day = date(year, month, calendar.monthrange(year, month)[1])
    
    # Get attendance records for the month
    monthly_attendance = employee.attendance_records.filter(
        date__gte=first_day,
        date__lte=last_day
    ).order_by('date')
    
    # Create calendar data
    cal = calendar.Calendar(firstweekday=6)  # Start on Sunday
    month_days = cal.monthdayscalendar(year, month)
    
    # Build attendance lookup
    attendance_dict = {a.date.day: a for a in monthly_attendance}
    
    # Calculate monthly stats
    present_count = monthly_attendance.filter(status='present').count()
    late_count = monthly_attendance.filter(status='late').count()
    absent_count = monthly_attendance.filter(status='absent').count()
    leave_count = monthly_attendance.filter(status='on_leave').count()
    
    today = date.today()
    is_current_month = (year == today.year and month == today.month)
    
    context = {
        'calendar_weeks': month_days,
        'attendance_dict': attendance_dict,
        'current_month': first_day.strftime('%B %Y'),
        'year': year,
        'month': month,
        'today': today.day if is_current_month else None,
        'monthly_stats': {
            'present': present_count,
            'late': late_count,
            'absent': absent_count,
            'on_leave': leave_count,
        },
    }
    
    return render(request, 'employees/partials/calendar.html', context)


@login_required
def request_attendance_correction(request):
    """Submit an attendance correction request."""
    employee = get_object_or_404(Employee, user=request.user)
    
    if request.method == 'POST':
        date_str = request.POST.get('date')
        requested_time_in = request.POST.get('time_in') or None
        requested_time_out = request.POST.get('time_out') or None
        requested_status = request.POST.get('requested_status') or ''
        reason = request.POST.get('reason')
        
        from datetime import datetime
        correction_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        # Get existing attendance record if any
        attendance = Attendance.objects.filter(employee=employee, date=correction_date).first()
        
        # Parse times
        time_in = None
        time_out = None
        if requested_time_in:
            time_in = datetime.strptime(requested_time_in, '%H:%M').time()
        if requested_time_out:
            time_out = datetime.strptime(requested_time_out, '%H:%M').time()
        
        AttendanceCorrection.objects.create(
            employee=employee,
            attendance=attendance,
            date=correction_date,
            current_time_in=attendance.time_in if attendance else None,
            current_time_out=attendance.time_out if attendance else None,
            current_status=attendance.status if attendance else '',
            requested_time_in=time_in,
            requested_time_out=time_out,
            requested_status=requested_status,
            reason=reason,
        )
        
        messages.success(request, 'Attendance correction request submitted successfully!')
        return redirect('employees:attendance')
    
    return redirect('employees:attendance')



@login_required
def notifications_view(request):
    """View all notifications for the logged-in employee."""
    employee = get_object_or_404(Employee, user=request.user)
    notifications = employee.notifications.all()[:50]
    
    # Mark as read
    if request.GET.get('mark_read'):
        employee.notifications.filter(is_read=False).update(is_read=True)
        return redirect('employees:notifications')
    
    context = {
        'notifications': notifications,
        'unread_count': employee.notifications.filter(is_read=False).count(),
    }
    return render(request, 'employees/notifications.html', context)


@login_required
def mark_notification_read(request, pk):
    """Mark a single notification as read."""
    employee = get_object_or_404(Employee, user=request.user)
    notification = get_object_or_404(Notification, pk=pk, recipient=employee)
    
    notification.is_read = True
    notification.save()
    
    if notification.link:
        return redirect(notification.link)
    return redirect('employees:notifications')