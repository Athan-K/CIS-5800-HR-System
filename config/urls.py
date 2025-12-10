"""
Main URL configuration for Ethos HRMS.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.accounts.views import dashboard_redirect

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Authentication (django-allauth)
    path('accounts/', include('allauth.urls')),
    
    # Custom auth views (2FA)
    path('auth/', include('apps.accounts.urls')),
    
    # Dashboard redirect
    path('', dashboard_redirect, name='dashboard'),
    
    # Employee portal
    path('employee/', include('apps.employees.urls')),
    
    # HR portal
    path('hr/', include('apps.hr.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])