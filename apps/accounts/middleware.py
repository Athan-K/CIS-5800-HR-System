from django.shortcuts import redirect


class TwoFactorMiddleware:
    """Middleware to enforce 2FA verification after login."""
    
    EXEMPT_URLS = [
        '/accounts/',
        '/auth/',
        '/admin/',
    ]
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Skip for unauthenticated users
        if not request.user.is_authenticated:
            return self.get_response(request)
        
        # Skip for exempt URLs
        path = request.path
        for exempt in self.EXEMPT_URLS:
            if path.startswith(exempt):
                return self.get_response(request)
        
        # Skip for static/media files
        if path.startswith('/static/') or path.startswith('/media/'):
            return self.get_response(request)
        
        # Check if 2FA is enabled but not verified
        if hasattr(request.user, 'two_factor_enabled') and request.user.two_factor_enabled:
            if not request.session.get('2fa_verified'):
                return redirect('verify_2fa')
        
        return self.get_response(request)
    
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib import messages


class TwoFactorMiddleware:
    """Middleware to enforce 2FA verification after login."""
    
    EXEMPT_URLS = [
        '/accounts/',
        '/auth/',
        '/admin/',
    ]
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Skip for unauthenticated users
        if not request.user.is_authenticated:
            return self.get_response(request)
        
        # Check if employee is terminated
        if hasattr(request.user, 'employee_profile') and request.user.employee_profile.status == 'terminated':
            messages.error(request, 'Your account has been terminated. Please contact HR.')
            logout(request)
            return redirect('account_login')
        
        # Skip for exempt URLs
        path = request.path
        for exempt in self.EXEMPT_URLS:
            if path.startswith(exempt):
                return self.get_response(request)
        
        # Skip for static/media files
        if path.startswith('/static/') or path.startswith('/media/'):
            return self.get_response(request)
        
        # Check if 2FA is enabled but not verified
        if hasattr(request.user, 'two_factor_enabled') and request.user.two_factor_enabled:
            if not request.session.get('2fa_verified'):
                return redirect('verify_2fa')
        
        return self.get_response(request)