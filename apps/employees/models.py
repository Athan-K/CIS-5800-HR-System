"""
Employee-related models including profiles, attendance, payslips, and leave requests.
"""

from django.db import models
from django.conf import settings
from simple_history.models import HistoricalRecords


class Department(models.Model):
    """Company departments."""
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    history = HistoricalRecords()
    
    def __str__(self):
        return self.name


class Employee(models.Model):
    """
    Employee profile information.
    Linked to User model for authentication.
    """
    
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        ON_LEAVE = 'on_leave', 'On Leave'
        TERMINATED = 'terminated', 'Terminated'
    
    # Link to user account
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='employee_profile'
    )
    
    # Basic info
    employee_id = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    
    # Work info
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        related_name='employees'
    )
    job_title = models.CharField(max_length=100)
    manager = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='direct_reports'
    )
    start_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE
    )
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Contact info
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    emergency_contact = models.CharField(max_length=100, blank=True)
    emergency_phone = models.CharField(max_length=20, blank=True)
    
    # Leave balances
    annual_leave_balance = models.DecimalField(max_digits=5, decimal_places=2, default=15.0)
    sick_leave_balance = models.DecimalField(max_digits=5, decimal_places=2, default=10.0)
    vacation_balance = models.DecimalField(max_digits=5, decimal_places=2, default=10.0)
    
    # Metadata
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Audit trail
    history = HistoricalRecords()
    
    class Meta:
        ordering = ['last_name', 'first_name']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.employee_id})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def email(self):
        return self.user.email


class Attendance(models.Model):
    """Daily attendance records."""
    
    class Status(models.TextChoices):
        PRESENT = 'present', 'Present'
        ABSENT = 'absent', 'Absent'
        LATE = 'late', 'Late'
        HALF_DAY = 'half_day', 'Half Day'
        ON_LEAVE = 'on_leave', 'On Leave'
    
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='attendance_records'
    )
    date = models.DateField()
    time_in = models.TimeField(null=True, blank=True)
    time_out = models.TimeField(null=True, blank=True)
    hours_worked = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PRESENT
    )
    notes = models.TextField(blank=True)
    
    history = HistoricalRecords()
    
    class Meta:
        unique_together = ['employee', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.employee} - {self.date}"


class Payslip(models.Model):
    """Employee payslips."""
    
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='payslips'
    )
    pay_period_start = models.DateField()
    pay_period_end = models.DateField()
    pay_date = models.DateField()
    
    # Amounts
    gross_pay = models.DecimalField(max_digits=10, decimal_places=2)
    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_pay = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Breakdown (stored as JSON for flexibility)
    details = models.JSONField(default=dict, blank=True)
    
    # PDF storage (optional)
    pdf_file = models.FileField(upload_to='payslips/', null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    history = HistoricalRecords()
    
    class Meta:
        ordering = ['-pay_date']
    
    def __str__(self):
        return f"{self.employee} - {self.pay_period_start} to {self.pay_period_end}"


class LeaveRequest(models.Model):
    """Employee leave requests."""
    
    class LeaveType(models.TextChoices):
        ANNUAL = 'annual', 'Annual Leave'
        SICK = 'sick', 'Sick Leave'
        VACATION = 'vacation', 'Vacation'
        UNPAID = 'unpaid', 'Unpaid Leave'
        OTHER = 'other', 'Other'
    
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'
        CANCELLED = 'cancelled', 'Cancelled'
    
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='leave_requests'
    )
    leave_type = models.CharField(
        max_length=20,
        choices=LeaveType.choices
    )
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    
    # Approval info
    reviewed_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_leave_requests'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    manager_notes = models.TextField(blank=True)
    
    # Metadata
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    history = HistoricalRecords()
    
    class Meta:
        ordering = ['-submitted_at']
    
    def __str__(self):
        return f"{self.employee} - {self.leave_type} ({self.start_date} to {self.end_date})"
    
    @property
    def days_requested(self):
        return (self.end_date - self.start_date).days + 1