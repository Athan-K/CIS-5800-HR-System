from django.urls import path
from . import views

app_name = 'hr'

urlpatterns = [
    path('', views.HRDashboardView.as_view(), name='dashboard'),
    
    # Employee management
    path('employees/', views.EmployeeListView.as_view(), name='employee_list'),
    path('employees/add/', views.EmployeeCreateView.as_view(), name='employee_create'),
    path('employees/<int:pk>/edit/', views.EmployeeUpdateView.as_view(), name='employee_update'),
    path('employees/<int:pk>/delete/', views.EmployeeDeleteView.as_view(), name='employee_delete'),
    
    path('leave/<int:pk>/review/', views.LeaveRequestReviewView.as_view(), name='leave_review'),
    path("leave/", views.LeaveListView.as_view(), name="leave_list"),
    path('settings/', views.HRSettingsView.as_view(), name='settings'),

    path('employees/<int:pk>/', views.EmployeeDetailView.as_view(), name='employee_detail'),

    # Department management
    path('departments/', views.DepartmentListView.as_view(), name='department_list'),
    path('departments/add/', views.DepartmentCreateView.as_view(), name='department_create'),
    path('departments/<int:pk>/edit/', views.DepartmentUpdateView.as_view(), name='department_update'),
    path('departments/<int:pk>/delete/', views.DepartmentDeleteView.as_view(), name='department_delete'),
    
    # Attendance corrections
    path('attendance-corrections/', views.AttendanceCorrectionListView.as_view(), name='attendance_corrections'),
    path('attendance-corrections/<int:pk>/approve/', views.approve_correction, name='approve_correction'),
    path('attendance-corrections/<int:pk>/reject/', views.reject_correction, name='reject_correction'),

    # Leave management
    path('leave-requests/', views.LeaveRequestListView.as_view(), name='leave_requests'),
    path('leave-requests/<int:pk>/approve/', views.approve_leave_request, name='approve_leave'),
    path('leave-requests/<int:pk>/reject/', views.reject_leave_request, name='reject_leave'),

    # Reports
    path('reports/', views.ReportsView.as_view(), name='reports'),
    path('api/reports/', views.generate_report, name='generate_report'),
    path('reports/generate/', views.GenerateReportView.as_view(), name='generate_report_page'),
]