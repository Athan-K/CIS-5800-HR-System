"""
Permission mixins for class-based views.
"""

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect


class HRRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin that requires user to be HR or Admin only - full access."""
    
    def test_func(self):
        return self.request.user.role in ['hr', 'admin']
    
    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            raise PermissionDenied("You don't have permission to access this page.")
        return super().handle_no_permission()


class ManagerRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin that requires user to be Manager, HR, or Admin - for leave requests and reports."""
    
    def test_func(self):
        return self.request.user.role in ['manager', 'hr', 'admin']
    
    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            raise PermissionDenied("You don't have permission to access this page.")
        return super().handle_no_permission()


class EmployeeRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin that requires user to have an employee profile."""
    
    def test_func(self):
        return hasattr(self.request.user, 'employee_profile')
    
    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            raise PermissionDenied("No employee profile found. Please contact HR.")
        return super().handle_no_permission()