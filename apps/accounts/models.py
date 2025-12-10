"""
Custom User model and related models for authentication.
"""

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    """Custom manager for User model with email as the unique identifier."""
    
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', User.Role.HR)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Custom User model using email instead of username.
    Includes role-based access control.
    """
    
    class Role(models.TextChoices):
        EMPLOYEE = 'employee', 'Employee'
        MANAGER = 'manager', 'Manager'
        HR = 'hr', 'HR Staff'
        ADMIN = 'admin', 'System Admin'
    
    username = None  # Remove username field
    email = models.EmailField('email address', unique=True)
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.EMPLOYEE,
    )
    must_change_password = models.BooleanField(default=False)
    two_factor_enabled = models.BooleanField(default=False)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
    
    def __str__(self):
        return self.email
    
    @property
    def is_hr(self):
        return self.role in [self.Role.HR, self.Role.ADMIN]
    
    @property
    def is_manager(self):
        return self.role in [self.Role.MANAGER, self.Role.HR, self.Role.ADMIN]