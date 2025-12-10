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
from .models import Employee, Attendance, Payslip, LeaveRequest
from .forms import LeaveRequestForm, ProfileUpdateForm


class EmployeeDashboardView(EmployeeRequiredMixin, TemplateView):
    """Employee dashboard showing overview of their information."""
    template_name = 'employees/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        employee = self.request.user.employee_profile
        
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
    """View attendance records."""
    employee = get_object_or_404(Employee, user=request.user)
    
    # Get filter parameters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    attendance = employee.attendance_records.all()
    
    if start_date:
        attendance = attendance.filter(date__gte=start_date)
    if end_date:
        attendance = attendance.filter(date__lte=end_date)
    
    return render(request, 'employees/attendance.html', {
        'employee': employee,
        'attendance_records': attendance,
    })


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
    """Submit and view leave requests."""
    employee = get_object_or_404(Employee, user=request.user)
    
    if request.method == 'POST':
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            leave_request = form.save(commit=False)
            leave_request.employee = employee
            leave_request.save()
            messages.success(request, 'Leave request submitted successfully!')
            return redirect('employees:leave_request')
    else:
        form = LeaveRequestForm()
    
    recent_requests = employee.leave_requests.all()[:10]
    
    return render(request, 'employees/leave_request.html', {
        'employee': employee,
        'form': form,
        'recent_requests': recent_requests,
        'leave_balances': {
            'annual': employee.annual_leave_balance,
            'vacation': employee.vacation_balance,
            'sick': employee.sick_leave_balance,
        },
    })


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