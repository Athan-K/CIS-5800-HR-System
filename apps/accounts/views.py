from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django_otp.plugins.otp_totp.models import TOTPDevice
import qrcode
import qrcode.image.svg
from io import BytesIO
import base64
from django.contrib.auth import logout

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from apps.employees.services import send_email_notification, get_base_url
from .models import User

@login_required
def dashboard_redirect(request):
    """Redirect to appropriate dashboard based on user role."""
    user = request.user
    
    # Check if employee is terminated
    try:
        if hasattr(user, 'employee_profile'):
            profile = user.employee_profile
            if profile and profile.status == 'terminated':
                messages.error(request, 'Your account has been terminated. Please contact HR.')
                logout(request)
                return redirect('account_login')
    except Exception:
        pass

    # HR, Admin, and Manager go to HR dashboard
    if user.role in ['hr', 'admin', 'manager']:
        return redirect('hr:dashboard')
    
    # Regular employees go to employee dashboard
    if hasattr(user, 'employee_profile'):
        return redirect('employees:dashboard')
    
    # Fallback - no employee profile found
    messages.error(request, 'No employee profile found. Please contact HR.')
    return redirect('account_login')

@login_required
def setup_2fa(request):
    """Setup two-factor authentication."""
    user = request.user
    
    # Check if user already has a device
    existing_device = TOTPDevice.objects.filter(user=user, confirmed=True).first()
    
    if existing_device:
        # User already has 2FA enabled, show management page
        return render(request, 'accounts/2fa_manage.html', {
            'device': existing_device,
        })
    
    # Get or create an unconfirmed device
    device, created = TOTPDevice.objects.get_or_create(
        user=user,
        confirmed=False,
        defaults={'name': f'{user.email} TOTP Device'}
    )
    
    if request.method == 'POST':
        token = request.POST.get('token', '').strip()
        
        if device.verify_token(token):
            # Token is valid, confirm the device
            device.confirmed = True
            device.save()
            
            # Update user's 2FA status
            user.two_factor_enabled = True
            user.save()
            
            messages.success(request, 'Two-factor authentication has been enabled successfully!')
            return redirect('2fa_manage')
        else:
            messages.error(request, 'Invalid verification code. Please try again.')
    
    # Generate QR code
    otpauth_url = device.config_url
    qr_code = generate_qr_code(otpauth_url)
    
    # Get the secret key for manual entry
    secret_key = base64.b32encode(device.bin_key).decode('utf-8')
    
    context = {
        'qr_code': qr_code,
        'secret_key': secret_key,
        'device': device,
    }
    return render(request, 'accounts/2fa_setup.html', context)


@login_required
def manage_2fa(request):
    """Manage existing 2FA settings."""
    user = request.user
    device = TOTPDevice.objects.filter(user=user, confirmed=True).first()
    
    if not device:
        return redirect('setup_2fa')
    
    return render(request, 'accounts/2fa_manage.html', {
        'device': device,
    })


@login_required
def disable_2fa(request):
    """Disable two-factor authentication."""
    if request.method == 'POST':
        user = request.user
        password = request.POST.get('password', '')
        
        if user.check_password(password):
            # Delete all TOTP devices for this user
            TOTPDevice.objects.filter(user=user).delete()
            
            # Update user's 2FA status
            user.two_factor_enabled = False
            user.save()
            
            messages.success(request, 'Two-factor authentication has been disabled.')
            return redirect('setup_2fa')
        else:
            messages.error(request, 'Incorrect password. Please try again.')
    
    return render(request, 'accounts/2fa_disable.html')


@login_required
def verify_2fa(request):
    """Verify 2FA token during login."""
    if request.method == 'POST':
        token = request.POST.get('token', '').strip()
        user = request.user
        
        device = TOTPDevice.objects.filter(user=user, confirmed=True).first()
        
        if device and device.verify_token(token):
            # Mark session as 2FA verified
            request.session['2fa_verified'] = True
            messages.success(request, 'Verification successful!')
            
            # Redirect to appropriate dashboard based on role
            if user.role in ['hr', 'admin', 'manager']:
                return redirect('hr:dashboard')
            else:
                return redirect('employees:dashboard')
        else:
            messages.error(request, 'Invalid verification code.')
    
    return render(request, 'accounts/2fa_verify.html')


def generate_qr_code(data):
    """Generate a QR code as base64 string."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"

def custom_password_reset(request):
    """Custom password reset that uses SendGrid HTTP API."""
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            
            # Generate reset token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Build reset URL
            base_url = get_base_url()
            reset_url = f"{base_url}/auth/password-reset/confirm/{uid}/{token}/"
            
            # Send email using HTTP API
            send_email_notification(
                to_email=email,
                subject='Password Reset - Ethos HRMS',
                template_name='emails/password_reset.html',
                context={
                    'user': user,
                    'reset_url': reset_url,
                    'base_url': base_url
                }
            )
            
            return redirect('custom_password_reset_done')
            
        except User.DoesNotExist:
            # Don't reveal if email exists - still show success
            return redirect('custom_password_reset_done')
    
    return render(request, 'account/password_reset.html')


def custom_password_reset_done(request):
    """Password reset email sent confirmation."""
    return render(request, 'account/password_reset_done.html')


def custom_password_reset_confirm(request, uidb64, token):
    """Confirm password reset with token."""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            
            if password1 and password1 == password2:
                user.set_password(password1)
                user.save()
                messages.success(request, 'Your password has been reset successfully!')
                return redirect('custom_password_reset_complete')
            else:
                messages.error(request, 'Passwords do not match.')
        
        return render(request, 'account/password_reset_from_key.html', {'validlink': True})
    else:
        return render(request, 'account/password_reset_from_key.html', {'validlink': False})


def custom_password_reset_complete(request):
    """Password reset complete."""
    return render(request, 'account/password_reset_from_key_done.html')