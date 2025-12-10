"""
Authentication views including 2FA setup and verification.
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django_otp.plugins.otp_totp.models import TOTPDevice
import qrcode
import qrcode.image.svg
from io import BytesIO
import base64


@login_required
def setup_2fa(request):
    """Set up two-factor authentication for the user."""
    user = request.user
    
    # Get or create TOTP device
    device, created = TOTPDevice.objects.get_or_create(
        user=user,
        name='default',
        defaults={'confirmed': False}
    )
    
    if request.method == 'POST':
        # Verify the token
        token = request.POST.get('token', '')
        if device.verify_token(token):
            device.confirmed = True
            device.save()
            user.two_factor_enabled = True
            user.save()
            messages.success(request, 'Two-factor authentication enabled successfully!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid token. Please try again.')
    
    # Generate QR code
    totp_uri = device.config_url
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(totp_uri)
    qr.make(fit=True)
    
    # Create QR code image
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    qr_code = base64.b64encode(buffer.getvalue()).decode()
    
    return render(request, 'accounts/setup_2fa.html', {
        'qr_code': qr_code,
        'secret_key': device.key,
    })


@login_required
def verify_2fa(request):
    """Verify 2FA token during login."""
    if request.method == 'POST':
        token = request.POST.get('token', '')
        device = TOTPDevice.objects.filter(user=request.user, confirmed=True).first()
        
        if device and device.verify_token(token):
            request.session['2fa_verified'] = True
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid token. Please try again.')
    
    return render(request, 'accounts/verify_2fa.html')


def dashboard_redirect(request):
    """Redirect to appropriate dashboard based on user role."""
    if not request.user.is_authenticated:
        return redirect('account_login')
    
    # Check if 2FA verification is needed
    if request.user.two_factor_enabled and not request.session.get('2fa_verified'):
        return redirect('verify_2fa')
    
    # Redirect based on role
    if request.user.is_hr:
        return redirect('hr:dashboard')
    else:
        return redirect('employees:dashboard')