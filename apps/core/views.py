from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required
def dashboard(request):
    """Redirect to appropriate dashboard based on user role."""
    user = request.user
    
    # HR, Admin, and Manager go to HR dashboard
    if user.role in ['hr', 'admin', 'manager']:
        return redirect('hr:dashboard')
    
    # Regular employees go to employee dashboard
    if hasattr(user, 'employee_profile'):
        return redirect('employees:dashboard')
    
    # Fallback - no employee profile found
    messages.error(request, 'No employee profile found. Please contact HR.')
    return redirect('account_login')