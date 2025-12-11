from django.urls import path
from . import views

urlpatterns = [
    path('2fa/setup/', views.setup_2fa, name='setup_2fa'),
    path('2fa/manage/', views.manage_2fa, name='2fa_manage'),
    path('2fa/disable/', views.disable_2fa, name='disable_2fa'),
    path('2fa/verify/', views.verify_2fa, name='verify_2fa'),
]