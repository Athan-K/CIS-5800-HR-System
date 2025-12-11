from django.urls import path
from . import views

app_name = 'employees'

urlpatterns = [
    path('dashboard/', views.EmployeeDashboardView.as_view(), name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('attendance/', views.attendance_view, name='attendance'),
    path('attendance/correction/', views.request_attendance_correction, name='request_correction'),
    path('payslips/', views.payslips_view, name='payslips'),
    path('leave/', views.leave_request_view, name='leave_request'),
    path('api/check-balance/', views.check_leave_balance, name='check_balance'),
    path('settings/', views.EmployeeSettingsView.as_view(), name='settings'),
    path('api/calendar/', views.attendance_calendar, name='attendance_calendar'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('notifications/<int:pk>/read/', views.mark_notification_read, name='mark_notification_read'),
]