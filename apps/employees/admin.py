from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Department, Employee, Attendance, Payslip, LeaveRequest, AttendanceCorrection


@admin.register(Department)
class DepartmentAdmin(SimpleHistoryAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name',)


@admin.register(Employee)
class EmployeeAdmin(SimpleHistoryAdmin):
    list_display = ('employee_id', 'first_name', 'last_name', 'department', 'job_title', 'status')
    list_filter = ('department', 'status')
    search_fields = ('first_name', 'last_name', 'employee_id', 'user__email')
    raw_id_fields = ('user', 'manager')


@admin.register(Attendance)
class AttendanceAdmin(SimpleHistoryAdmin):
    list_display = ('employee', 'date', 'time_in', 'time_out', 'status')
    list_filter = ('status', 'date')
    search_fields = ('employee__first_name', 'employee__last_name')


@admin.register(Payslip)
class PayslipAdmin(SimpleHistoryAdmin):
    list_display = ('employee', 'pay_period_start', 'pay_period_end', 'gross_pay', 'net_pay')
    list_filter = ('pay_date',)
    search_fields = ('employee__first_name', 'employee__last_name')


@admin.register(LeaveRequest)
class LeaveRequestAdmin(SimpleHistoryAdmin):
    list_display = ('employee', 'leave_type', 'start_date', 'end_date', 'status')
    list_filter = ('status', 'leave_type')
    search_fields = ('employee__first_name', 'employee__last_name')

@admin.register(AttendanceCorrection)
class AttendanceCorrectionAdmin(SimpleHistoryAdmin):
    list_display = ('employee', 'date', 'status', 'submitted_at')
    list_filter = ('status', 'submitted_at')
    search_fields = ('employee__first_name', 'employee__last_name')