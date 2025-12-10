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
from apps.employees.models import Employee, Department, LeaveRequest, Attendance
from .forms import EmployeeForm, EmployeeSearchForm
from apps.employees.models import Employee, Department, LeaveRequest, Attendance
from datetime import datetime, timedelta

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
        context['pending_requests'] = LeaveRequest.objects.filter(
            status=LeaveRequest.Status.PENDING
        ).select_related('employee')[:5]
        
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
        
        # Filter by role/status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['departments'] = Department.objects.all()
        context['search_form'] = EmployeeSearchForm(self.request.GET)
        return context


class EmployeeCreateView(HRRequiredMixin, CreateView):
    """Create new employee."""
    model = Employee
    form_class = EmployeeForm
    template_name = 'hr/employee_form.html'
    success_url = reverse_lazy('hr:employee_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Employee created successfully!')
        return super().form_valid(form)


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
    """Generate and view reports."""
    template_name = 'hr/reports.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Default date range (last 30 days)
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
        
        # Available report types
        context['report_types'] = [
            ('headcount', 'Headcount Report'),
            ('department', 'Department Summary'),
            ('leave', 'Leave Report'),
            ('attendance', 'Attendance Report'),
        ]
        
        context['departments'] = Department.objects.all()
        context['default_start_date'] = start_date
        context['default_end_date'] = end_date
        
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
        )


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

def generate_report(request):
    """Generate report data based on parameters."""
    report_type = request.GET.get('report_type')
    department_id = request.GET.get('department')
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    
    # Parse dates
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None
    
    context = {'report_type': report_type}
    
    if report_type == 'headcount':
        employees = Employee.objects.filter(status=Employee.Status.ACTIVE)
        if department_id:
            employees = employees.filter(department_id=department_id)
        
        by_department = Department.objects.annotate(
            active_count=Count('employees', filter=Q(employees__status=Employee.Status.ACTIVE)),
            on_leave_count=Count('employees', filter=Q(employees__status=Employee.Status.ON_LEAVE)),
            terminated_count=Count('employees', filter=Q(employees__status=Employee.Status.TERMINATED))
        ).order_by('name')
        
        context.update({
            'total_employees': employees.count(),
            'total_active': Employee.objects.filter(status=Employee.Status.ACTIVE).count(),
            'total_on_leave': Employee.objects.filter(status=Employee.Status.ON_LEAVE).count(),
            'total_terminated': Employee.objects.filter(status=Employee.Status.TERMINATED).count(),
            'departments': by_department,
        })
    
    elif report_type == 'department':
        departments = Department.objects.annotate(
            employee_count=Count('employees', filter=Q(employees__status=Employee.Status.ACTIVE)),
            avg_salary=Avg('employees__salary', filter=Q(employees__status=Employee.Status.ACTIVE))
        ).order_by('-employee_count')
        
        context.update({
            'departments': departments,
            'total_departments': departments.count(),
        })
    
    elif report_type == 'leave':
        leaves = LeaveRequest.objects.all()
        if department_id:
            leaves = leaves.filter(employee__department_id=department_id)
        if start_date:
            leaves = leaves.filter(start_date__gte=start_date)
        if end_date:
            leaves = leaves.filter(end_date__lte=end_date)
        
        by_type = leaves.values('leave_type').annotate(
            count=Count('id'),
            total_days=Sum('id')  # This should calculate actual days
        ).order_by('-count')
        
        by_status = leaves.values('status').annotate(
            count=Count('id')
        ).order_by('-count')
        
        context.update({
            'total_requests': leaves.count(),
            'pending': leaves.filter(status=LeaveRequest.Status.PENDING).count(),
            'approved': leaves.filter(status=LeaveRequest.Status.APPROVED).count(),
            'rejected': leaves.filter(status=LeaveRequest.Status.REJECTED).count(),
            'by_type': by_type,
            'by_status': by_status,
            'recent_requests': leaves.order_by('-submitted_at')[:10],
        })
    
    elif report_type == 'attendance':
        attendance = Attendance.objects.all()
        if department_id:
            attendance = attendance.filter(employee__department_id=department_id)
        if start_date:
            attendance = attendance.filter(date__gte=start_date)
        if end_date:
            attendance = attendance.filter(date__lte=end_date)
        
        by_status = attendance.values('status').annotate(
            count=Count('id')
        ).order_by('-count')
        
        total_hours = attendance.aggregate(Sum('hours_worked'))['hours_worked__sum'] or 0
        total_days = attendance.count()
        avg_hours = total_hours / total_days if total_days > 0 else 0
        
        context.update({
            'total_records': attendance.count(),
            'present': attendance.filter(status=Attendance.Status.PRESENT).count(),
            'absent': attendance.filter(status=Attendance.Status.ABSENT).count(),
            'late': attendance.filter(status=Attendance.Status.LATE).count(),
            'on_leave': attendance.filter(status=Attendance.Status.ON_LEAVE).count(),
            'total_hours': round(total_hours, 2),
            'avg_hours_per_day': round(avg_hours, 2),
            'by_status': by_status,
        })
    
    # Render the appropriate partial template
    template_name = f'hr/reports/{report_type}_report.html'
    return render(request, template_name, context)