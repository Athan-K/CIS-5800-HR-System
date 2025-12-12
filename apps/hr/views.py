"""
HR management views.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from django.http import JsonResponse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from apps.core.mixins import HRRequiredMixin, ManagerRequiredMixin
from apps.employees.models import Employee, Department, LeaveRequest, Attendance, AttendanceCorrection
from .forms import EmployeeForm, EmployeeSearchForm
from datetime import datetime, timedelta
from django.db.models import Avg, Sum
from django.contrib.auth.decorators import login_required
from apps.employees.services import (
    notify_leave_approved, 
    notify_leave_rejected,
    notify_correction_approved,
    notify_correction_rejected
)

class HRDashboardView(HRRequiredMixin, TemplateView):
    """HR Dashboard with overview statistics."""
    template_name = 'hr/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Employee statistics
        context['total_employees'] = Employee.objects.filter(
            status=Employee.Status.ACTIVE
        ).count()
        context['on_leave'] = Employee.objects.filter(
            status=Employee.Status.ON_LEAVE
        ).count()
        
        # Department breakdown
        context['departments'] = Department.objects.annotate(
            employee_count=Count('employees', filter=Q(employees__status=Employee.Status.ACTIVE))
        )
        
        # Pending leave requests
        pending_leaves = LeaveRequest.objects.filter(
            status=LeaveRequest.Status.PENDING
        ).select_related('employee', 'employee__department').order_by('-submitted_at')
        context['pending_leave_requests'] = pending_leaves[:5]
        context['pending_leave_count'] = pending_leaves.count()
        
        # Pending attendance corrections
        pending_corrections = AttendanceCorrection.objects.filter(
            status=AttendanceCorrection.Status.PENDING
        ).select_related('employee', 'employee__department').order_by('-submitted_at')
        context['pending_corrections'] = pending_corrections[:5]
        context['pending_correction_count'] = pending_corrections.count()
        
        # Total pending items for badge
        context['total_pending'] = context['pending_leave_count'] + context['pending_correction_count']
        
        # Recent activity (from audit log)
        context['recent_changes'] = Employee.history.all()[:10]
        
        return context


class EmployeeListView(HRRequiredMixin, ListView):
    """List all employees with search and filter."""
    model = Employee
    template_name = 'hr/employee_list.html'
    context_object_name = 'employees'
    paginate_by = 15
    
    def get_queryset(self):
        queryset = Employee.objects.select_related('department', 'user')
        
        # Search
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(employee_id__icontains=search) |
                Q(user__email__icontains=search)
            )
        
        # Filter by department
        department = self.request.GET.get('department')
        if department:
            queryset = queryset.filter(department_id=department)
        
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        #Filter by role
        role = self.request.GET.get('role')
        if role:
            queryset = queryset.filter(user__role=role)   
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['departments'] = Department.objects.all()
        context['search_form'] = EmployeeSearchForm(self.request.GET)
        return context


from apps.employees.services import send_welcome_email

class EmployeeCreateView(HRRequiredMixin, CreateView):
    """Create a new employee."""
    model = Employee
    form_class = EmployeeForm
    template_name = 'hr/employee_form.html'
    success_url = reverse_lazy('hr:employee_list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        if hasattr(form, 'generated_password'):
            employee = form.instance
            password = form.generated_password
            
            # Send welcome email with credentials
            send_welcome_email(employee, password)
            
            messages.success(
                self.request, 
                f'Employee "{employee.full_name}" created successfully! '
                f'Login credentials - Email: {employee.user.email} | '
                f'Temporary Password: {password} | '
                f'A welcome email has been sent.'
            )
        else:
            messages.success(self.request, f'Employee created successfully!')
        
        return response


class EmployeeUpdateView(HRRequiredMixin, UpdateView):
    """Update employee details."""
    model = Employee
    form_class = EmployeeForm
    template_name = 'hr/employee_form.html'
    success_url = reverse_lazy('hr:employee_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Employee updated successfully!')
        return super().form_valid(form)


class EmployeeDeleteView(HRRequiredMixin, DeleteView):
    """Delete employee (with confirmation)."""
    model = Employee
    template_name = 'hr/employee_confirm_delete.html'
    success_url = reverse_lazy('hr:employee_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Employee deleted successfully!')
        return super().delete(request, *args, **kwargs)


class ReportsView(ManagerRequiredMixin, TemplateView):
    """Generate and view reports with visualizations."""
    template_name = 'hr/reports.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Department breakdown
        departments = Department.objects.annotate(
            employee_count=Count('employees', filter=Q(employees__status=Employee.Status.ACTIVE))
        )
        context['departments'] = departments
        context['department_names'] = [d.name for d in departments]
        context['department_counts'] = [d.employee_count for d in departments]
        
        # Employee statistics
        context['total_employees'] = Employee.objects.filter(status=Employee.Status.ACTIVE).count()
        context['on_leave'] = Employee.objects.filter(status=Employee.Status.ON_LEAVE).count()
        context['total_terminated'] = Employee.objects.filter(status=Employee.Status.TERMINATED).count()
        
        # Leave request statistics
        context['pending_leaves'] = LeaveRequest.objects.filter(status=LeaveRequest.Status.PENDING).count()
        context['approved_leaves'] = LeaveRequest.objects.filter(status=LeaveRequest.Status.APPROVED).count()
        context['rejected_leaves'] = LeaveRequest.objects.filter(status=LeaveRequest.Status.REJECTED).count()
        
        # Leave by type
        leave_by_type = LeaveRequest.objects.values('leave_type').annotate(count=Count('id'))
        context['leave_types'] = [item['leave_type'].title() for item in leave_by_type]
        context['leave_type_counts'] = [item['count'] for item in leave_by_type]
        
        # Headcount by month (last 6 months) - based on start_date
        from datetime import date
        from dateutil.relativedelta import relativedelta
        
        monthly_data = []
        month_labels = []
        
        for i in range(5, -1, -1):
            target_date = date.today() - relativedelta(months=i)
            month_labels.append(target_date.strftime('%b %Y'))
            count = Employee.objects.filter(
                start_date__lte=target_date,
                status__in=[Employee.Status.ACTIVE, Employee.Status.ON_LEAVE]
            ).count()
            monthly_data.append(count)
        
        context['month_labels'] = month_labels
        context['monthly_headcount'] = monthly_data
        
        # Salary distribution by department
        from django.db.models import Avg, Sum
        salary_by_dept = Department.objects.annotate(
            avg_salary=Avg('employees__salary', filter=Q(employees__status=Employee.Status.ACTIVE)),
            total_salary=Sum('employees__salary', filter=Q(employees__status=Employee.Status.ACTIVE))
        )
        context['salary_dept_names'] = [d.name for d in salary_by_dept if d.avg_salary]
        context['salary_averages'] = [float(d.avg_salary or 0) for d in salary_by_dept if d.avg_salary]
        
        # Tenure distribution
        from datetime import date
        tenure_ranges = {
            '< 1 year': 0,
            '1-2 years': 0,
            '2-3 years': 0,
            '3-5 years': 0,
            '5+ years': 0,
        }
        
        for emp in Employee.objects.filter(status=Employee.Status.ACTIVE):
            years = (date.today() - emp.start_date).days / 365
            if years < 1:
                tenure_ranges['< 1 year'] += 1
            elif years < 2:
                tenure_ranges['1-2 years'] += 1
            elif years < 3:
                tenure_ranges['2-3 years'] += 1
            elif years < 5:
                tenure_ranges['3-5 years'] += 1
            else:
                tenure_ranges['5+ years'] += 1
        
        context['tenure_labels'] = list(tenure_ranges.keys())
        context['tenure_counts'] = list(tenure_ranges.values())
        
        # Recent hires (last 30 days)
        from datetime import timedelta
        thirty_days_ago = date.today() - timedelta(days=30)
        context['recent_hires'] = Employee.objects.filter(
            start_date__gte=thirty_days_ago
        ).order_by('-start_date')[:5]
        
        # Attendance summary (last 7 days)
        seven_days_ago = date.today() - timedelta(days=7)
        attendance_stats = Attendance.objects.filter(date__gte=seven_days_ago).values('status').annotate(count=Count('id'))
        context['attendance_stats'] = {item['status']: item['count'] for item in attendance_stats}
        
        return context

class DepartmentCreateView(HRRequiredMixin, CreateView):
    """Create new department."""
    model = Department
    fields = ['name', 'description']
    template_name = 'hr/department_form.html'
    success_url = reverse_lazy('hr:dashboard')
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['name'].widget.attrs.update({
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500'
        })
        form.fields['description'].widget.attrs.update({
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500',
            'rows': 3
        })
        return form
    
    def form_valid(self, form):
        messages.success(self.request, 'Department created successfully!')
        return super().form_valid(form)

class DepartmentListView(HRRequiredMixin, ListView):
    """List all departments."""
    model = Department
    template_name = 'hr/department_list.html'
    context_object_name = 'departments'
    
    def get_queryset(self):
        return Department.objects.annotate(
            employee_count=Count('employees', filter=Q(employees__status=Employee.Status.ACTIVE))
        ).order_by('name')


class DepartmentUpdateView(HRRequiredMixin, UpdateView):
    """Update department."""
    model = Department
    fields = ['name', 'description']
    template_name = 'hr/department_form.html'
    success_url = reverse_lazy('hr:department_list')
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['name'].widget.attrs.update({
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500'
        })
        form.fields['description'].widget.attrs.update({
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500',
            'rows': 3
        })
        return form
    
    def form_valid(self, form):
        messages.success(self.request, 'Department updated successfully!')
        return super().form_valid(form)


class DepartmentDeleteView(HRRequiredMixin, DeleteView):
    """Delete department."""
    model = Department
    template_name = 'hr/department_confirm_delete.html'
    success_url = reverse_lazy('hr:department_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Department deleted successfully!')
        return super().delete(request, *args, **kwargs)
    
class DepartmentCreateView(HRRequiredMixin, CreateView):
    """Create new department."""
    model = Department
    fields = ['name', 'description']
    template_name = 'hr/department_form.html'
    success_url = reverse_lazy('hr:department_list')  # Changed from dashboard
    
    # ... rest stays the same

class LeaveRequestReviewView(HRRequiredMixin, UpdateView):
    model = LeaveRequest
    fields = ["status", "manager_notes"]
    template_name = "hr/leave_review.html"

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.reviewed_by = self.request.user.employee_profile
        obj.reviewed_at = timezone.now()
        obj.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("hr:dashboard")
    

class LeaveListView(HRRequiredMixin, ListView):
    model = LeaveRequest
    template_name = "hr/leave_list.html"
    context_object_name = "leave_requests"

    def get_queryset(self):
        return LeaveRequest.objects.select_related("employee").order_by("-start_date")

class OnLeaveTodayView(HRRequiredMixin, ListView):
    model = LeaveRequest
    template_name = "hr/on_leave_today.html"
    context_object_name = "leave_requests"

    def get_queryset(self):
        today = timezone.localdate()
        return LeaveRequest.objects.filter(
            status="approved",
            start_date__lte=today,
            end_date__gte=today
        ).select_related("employee").order_by("employee__last_name")

class HRSettingsView(HRRequiredMixin, TemplateView):
    """HR Settings page."""
    template_name = 'hr/settings.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context


class LeaveRequestListView(HRRequiredMixin, ListView):
    """List all leave requests for HR to manage."""
    model = LeaveRequest
    template_name = 'hr/leave_requests.html'
    context_object_name = 'leave_requests'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = LeaveRequest.objects.select_related('employee', 'employee__department').order_by('-submitted_at')
        
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by department
        department = self.request.GET.get('department')
        if department:
            queryset = queryset.filter(employee__department_id=department)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['departments'] = Department.objects.all()
        context['pending_count'] = LeaveRequest.objects.filter(status=LeaveRequest.Status.PENDING).count()
        context['current_status'] = self.request.GET.get('status', '')
        context['current_department'] = self.request.GET.get('department', '')
        return context


@login_required
def approve_leave_request(request, pk):
    """Approve a leave request."""
    if not request.user.is_hr:
        raise PermissionDenied
    
    leave_request = get_object_or_404(LeaveRequest, pk=pk)
    
    if request.method == 'POST':
        leave_request.status = LeaveRequest.Status.APPROVED
        leave_request.reviewed_by = request.user.employee_profile if hasattr(request.user, 'employee_profile') else None
        leave_request.reviewed_at = timezone.now()
        leave_request.manager_notes = request.POST.get('notes', '')
        leave_request.save()
        
        # Deduct from leave balance
        employee = leave_request.employee
        days = leave_request.days_requested
        
        if leave_request.leave_type == 'annual':
            employee.annual_leave_balance -= days
        elif leave_request.leave_type == 'vacation':
            employee.vacation_balance -= days
        elif leave_request.leave_type == 'sick':
            employee.sick_leave_balance -= days
        employee.save()
        
        # Send notification
        notify_leave_approved(leave_request)
        
        messages.success(request, f'Leave request approved for {employee.full_name}')
    
    # Check if request came from employee detail page
    next_url = request.POST.get('next') or request.GET.get('next')
    if next_url:
        return redirect(next_url)
    return redirect('hr:leave_requests')

@login_required
def reject_leave_request(request, pk):
    """Reject a leave request."""
    if not request.user.is_hr:
        raise PermissionDenied
    
    leave_request = get_object_or_404(LeaveRequest, pk=pk)
    
    if request.method == 'POST':
        leave_request.status = LeaveRequest.Status.REJECTED
        leave_request.reviewed_by = request.user.employee_profile if hasattr(request.user, 'employee_profile') else None
        leave_request.reviewed_at = timezone.now()
        leave_request.manager_notes = request.POST.get('notes', '')
        leave_request.save()
        
        # Send notification
        notify_leave_rejected(leave_request)
        
        messages.success(request, f'Leave request rejected for {leave_request.employee.full_name}')
    
    next_url = request.POST.get('next') or request.GET.get('next')
    if next_url:
        return redirect(next_url)
    return redirect('hr:leave_requests')



class GenerateReportView(ManagerRequiredMixin, TemplateView):
    """Page for generating filtered reports."""
    template_name = 'hr/generate_report.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['departments'] = Department.objects.all()
        return context



@login_required
def generate_report(request):
    """Generate report data based on parameters."""
    from datetime import datetime
    from django.db.models import Avg, Sum
    
    # Handle both GET and POST requests
    params = request.POST if request.method == 'POST' else request.GET
    
    report_type = params.get('report_type')
    department_id = params.get('department')
    start_date_str = params.get('start_date')
    end_date_str = params.get('end_date')
    
    # If no report type, show the form
    if not report_type:
        return render(request, 'hr/generate_report.html', {
            'departments': Department.objects.all()
        })
    
    # Parse dates safely
    start_date = None
    end_date = None
    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        except ValueError:
            pass
    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            pass
    
    context = {
        'report_type': report_type,
        'start_date': start_date,
        'end_date': end_date,
        'departments': Department.objects.all(),
    }
    
    if report_type == 'headcount':
        employees = Employee.objects.all()
        if department_id:
            employees = employees.filter(department_id=department_id)
        
        by_department = Department.objects.annotate(
            active_count=Count('employees', filter=Q(employees__status=Employee.Status.ACTIVE)),
            on_leave_count=Count('employees', filter=Q(employees__status=Employee.Status.ON_LEAVE)),
            terminated_count=Count('employees', filter=Q(employees__status=Employee.Status.TERMINATED))
        ).order_by('name')
        
        dept_names = [d.name for d in by_department]
        dept_active = [d.active_count for d in by_department]
        
        context.update({
            'total_employees': employees.filter(status=Employee.Status.ACTIVE).count(),
            'total_active': Employee.objects.filter(status=Employee.Status.ACTIVE).count(),
            'total_on_leave': Employee.objects.filter(status=Employee.Status.ON_LEAVE).count(),
            'total_terminated': Employee.objects.filter(status=Employee.Status.TERMINATED).count(),
            'by_department': by_department,
            'dept_names': dept_names,
            'dept_active': dept_active,
        })
        return render(request, 'hr/reports/headcount_report.html', context)
    
    elif report_type == 'department':
        departments = Department.objects.annotate(
            employee_count=Count('employees', filter=Q(employees__status=Employee.Status.ACTIVE)),
            avg_salary=Avg('employees__salary', filter=Q(employees__status=Employee.Status.ACTIVE)),
            total_salary=Sum('employees__salary', filter=Q(employees__status=Employee.Status.ACTIVE))
        ).order_by('-employee_count')
    
        dept_names = list(departments.values_list('name', flat=True))
        dept_counts = [d.employee_count for d in departments]
        dept_salaries = [float(d.avg_salary) if d.avg_salary else 0 for d in departments]
    
        context.update({
            'department_list': departments,
            'total_departments': departments.count(),
            'dept_names': dept_names,
            'dept_counts': dept_counts,
            'dept_salaries': dept_salaries,
        })
        return render(request, 'hr/reports/department_report.html', context)
    
    elif report_type == 'leave':
        leaves = LeaveRequest.objects.all()
        if department_id:
            leaves = leaves.filter(employee__department_id=department_id)
        if start_date:
            leaves = leaves.filter(start_date__gte=start_date)
        if end_date:
            leaves = leaves.filter(end_date__lte=end_date)
        
        by_type = leaves.values('leave_type').annotate(count=Count('id')).order_by('-count')
        by_status = leaves.values('status').annotate(count=Count('id')).order_by('-count')
        
        type_labels = [item['leave_type'].title() for item in by_type]
        type_counts = [item['count'] for item in by_type]
        
        pending = leaves.filter(status=LeaveRequest.Status.PENDING).count()
        approved = leaves.filter(status=LeaveRequest.Status.APPROVED).count()
        rejected = leaves.filter(status=LeaveRequest.Status.REJECTED).count()
        
        context.update({
            'total_requests': leaves.count(),
            'pending': pending,
            'approved': approved,
            'rejected': rejected,
            'by_type': by_type,
            'by_status': by_status,
            'recent_requests': leaves.order_by('-submitted_at')[:10],
            'type_labels': type_labels,
            'type_counts': type_counts,
        })
        return render(request, 'hr/reports/leave_report.html', context)
    
    elif report_type == 'attendance':
        attendance = Attendance.objects.all()
        if department_id:
            attendance = attendance.filter(employee__department_id=department_id)
        if start_date:
            attendance = attendance.filter(date__gte=start_date)
        if end_date:
            attendance = attendance.filter(date__lte=end_date)
        
        present = attendance.filter(status=Attendance.Status.PRESENT).count()
        absent = attendance.filter(status=Attendance.Status.ABSENT).count()
        late = attendance.filter(status=Attendance.Status.LATE).count()
        on_leave = attendance.filter(status=Attendance.Status.ON_LEAVE).count()
        half_day = attendance.filter(status=Attendance.Status.HALF_DAY).count()
        
        total_hours = attendance.aggregate(Sum('hours_worked'))['hours_worked__sum'] or 0
        total_days = attendance.count()
        avg_hours = float(total_hours) / total_days if total_days > 0 else 0
        
        context.update({
            'total_records': total_days,
            'present': present,
            'absent': absent,
            'late': late,
            'on_leave': on_leave,
            'half_day': half_day,
            'total_hours': round(float(total_hours), 2),
            'avg_hours_per_day': round(avg_hours, 2),
        })
        return render(request, 'hr/reports/attendance_report.html', context)
    
    else:
        return render(request, 'hr/reports/no_report.html', context)

class AttendanceCorrectionListView(HRRequiredMixin, ListView):
    """List all attendance correction requests."""
    model = AttendanceCorrection
    template_name = 'hr/attendance_corrections.html'
    context_object_name = 'corrections'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = AttendanceCorrection.objects.select_related(
            'employee', 'employee__department'
        ).order_by('-submitted_at')
        
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pending_count'] = AttendanceCorrection.objects.filter(status='pending').count()
        context['current_status'] = self.request.GET.get('status', '')
        return context


@login_required
def approve_correction(request, pk):
    """Approve an attendance correction."""
    if not request.user.is_hr:
        raise PermissionDenied
    
    correction = get_object_or_404(AttendanceCorrection, pk=pk)
    
    if request.method == 'POST':
        # Get or create the attendance record for that date
        attendance, created = Attendance.objects.get_or_create(
            employee=correction.employee,
            date=correction.date,
            defaults={
                'status': correction.requested_status or Attendance.Status.PRESENT,
                'time_in': correction.requested_time_in,
                'time_out': correction.requested_time_out,
            }
        )
        
        # If record already existed, update it
        if not created:
            if correction.requested_time_in:
                attendance.time_in = correction.requested_time_in
            if correction.requested_time_out:
                attendance.time_out = correction.requested_time_out
            if correction.requested_status:
                attendance.status = correction.requested_status
        
        # Calculate hours worked
        if attendance.time_in and attendance.time_out:
            from datetime import datetime, timedelta
            time_in_dt = datetime.combine(correction.date, attendance.time_in)
            time_out_dt = datetime.combine(correction.date, attendance.time_out)
            
            if time_out_dt < time_in_dt:
                time_out_dt += timedelta(days=1)
            
            hours = (time_out_dt - time_in_dt).total_seconds() / 3600
            attendance.hours_worked = round(hours, 2)
        
        attendance.save()
        
        # Update correction status
        correction.status = AttendanceCorrection.Status.APPROVED
        correction.reviewed_by = request.user.employee_profile if hasattr(request.user, 'employee_profile') else None
        correction.reviewed_at = timezone.now()
        correction.reviewer_notes = request.POST.get('notes', '')
        correction.attendance = attendance
        correction.save()
        
        # Send notification
        notify_correction_approved(correction)
        
        messages.success(request, f'Correction approved for {correction.employee.full_name}. Attendance updated.')
    
    next_url = request.POST.get('next') or request.GET.get('next')
    if next_url:
        return redirect(next_url)
    return redirect('hr:attendance_corrections')


@login_required
def reject_correction(request, pk):
    """Reject an attendance correction."""
    if not request.user.is_hr:
        raise PermissionDenied
    
    correction = get_object_or_404(AttendanceCorrection, pk=pk)
    
    if request.method == 'POST':
        correction.status = AttendanceCorrection.Status.REJECTED
        correction.reviewed_by = request.user.employee_profile if hasattr(request.user, 'employee_profile') else None
        correction.reviewed_at = timezone.now()
        correction.reviewer_notes = request.POST.get('notes', '')
        correction.save()
        
        # Send notification
        notify_correction_rejected(correction)
        
        messages.success(request, f'Correction rejected for {correction.employee.full_name}')
    
    next_url = request.POST.get('next') or request.GET.get('next')
    if next_url:
        return redirect(next_url)
    return redirect('hr:attendance_corrections')


class EmployeeDetailView(HRRequiredMixin, TemplateView):
    """Detailed employee profile view for HR."""
    template_name = 'hr/employee_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        employee = get_object_or_404(Employee, pk=self.kwargs['pk'])
        
        # Get leave requests
        leave_requests = employee.leave_requests.all().order_by('-submitted_at')
        pending_leaves = leave_requests.filter(status=LeaveRequest.Status.PENDING)
        
        # Get attendance records (last 30 days)
        from datetime import date, timedelta
        thirty_days_ago = date.today() - timedelta(days=30)
        recent_attendance = employee.attendance_records.filter(
            date__gte=thirty_days_ago
        ).order_by('-date')
        
        # Get attendance corrections
        corrections = employee.attendance_corrections.all().order_by('-submitted_at')[:10]
        
        # Calculate attendance stats
        total_attendance = recent_attendance.count()
        present_days = recent_attendance.filter(status=Attendance.Status.PRESENT).count()
        late_days = recent_attendance.filter(status=Attendance.Status.LATE).count()
        absent_days = recent_attendance.filter(status=Attendance.Status.ABSENT).count()
        
        # Get payslips
        payslips = employee.payslips.all().order_by('-pay_date')[:6]
        
        # Get employment history from audit log
        history = employee.history.all()[:10]
        
        context.update({
            'employee': employee,
            'leave_requests': leave_requests[:10],
            'pending_leaves': pending_leaves,
            'pending_leave_count': pending_leaves.count(),
            'recent_attendance': recent_attendance[:15],
            'corrections': corrections,
            'payslips': payslips,
            'history': history,
            'attendance_stats': {
                'total': total_attendance,
                'present': present_days,
                'late': late_days,
                'absent': absent_days,
                'attendance_rate': round((present_days + late_days) / total_attendance * 100, 1) if total_attendance > 0 else 0,
            },
            'leave_balances': {
                'annual': employee.annual_leave_balance,
                'vacation': employee.vacation_balance,
                'sick': employee.sick_leave_balance,
            },
        })
        return context