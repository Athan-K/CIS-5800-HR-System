"""
Permission decorators for function-based views.
"""

from functools import wraps
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect


def hr_required(view_func):
    """Decorator that requires user to be HR staff."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('account_login')
        if not request.user.is_hr:
            raise PermissionDenied("You don't have permission to access this page.")
        return view_func(request, *args, **kwargs)
    return wrapper


def manager_required(view_func):
    """Decorator that requires user to be a manager or HR."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('account_login')
        if not request.user.is_manager:
            raise PermissionDenied("You don't have permission to access this page.")
        return view_func(request, *args, **kwargs)
    return wrapper