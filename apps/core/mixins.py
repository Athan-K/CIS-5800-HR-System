"""
Permission mixins for class-based views.
"""

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect


class HRRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin that requires user to be HR staff."""
    
    def test_func(self):
        return self.request.user.is_hr
    
    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            raise PermissionDenied("You don't have permission to access this page.")
        return super().handle_no_permission()


class ManagerRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin that requires user to be a manager or HR."""
    
    def test_func(self):
        return self.request.user.is_manager
    
    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            raise PermissionDenied("You don't have permission to access this page.")
        return super().handle_no_permission()


class EmployeeRequiredMixin(LoginRequiredMixin):
    """Mixin that requires user to have an employee profile."""
    
    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, 'employee_profile'):
            return redirect('no_profile')
        return super().dispatch(request, *args, **kwargs)