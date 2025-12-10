from django.urls import path
from . import views

app_name = 'employees'

urlpatterns = [
    path('dashboard/', views.EmployeeDashboardView.as_view(), name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('attendance/', views.attendance_view, name='attendance'),
    path('payslips/', views.payslips_view, name='payslips'),
    path('leave/', views.leave_request_view, name='leave_request'),
    path('api/check-balance/', views.check_leave_balance, name='check_balance'),
]