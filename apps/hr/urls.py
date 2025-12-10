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

    # Department management
    path('departments/', views.DepartmentListView.as_view(), name='department_list'),
    path('departments/add/', views.DepartmentCreateView.as_view(), name='department_create'),
    path('departments/<int:pk>/edit/', views.DepartmentUpdateView.as_view(), name='department_update'),
    path('departments/<int:pk>/delete/', views.DepartmentDeleteView.as_view(), name='department_delete'),
    
    # Reports
    path('reports/', views.ReportsView.as_view(), name='reports'),
    path('api/reports/', views.generate_report, name='generate_report'),
]