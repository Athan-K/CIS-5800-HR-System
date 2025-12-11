"""
Forms for HR management.
"""

from django import forms
from django.contrib.auth import get_user_model
from apps.employees.models import Employee, Department
import secrets

User = get_user_model()


class EmployeeForm(forms.ModelForm):
    """Form for creating and editing employees."""
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500',
            'placeholder': 'employee@ethos.com'
        })
    )
    role = forms.ChoiceField(
        choices=[
            ('employee', 'Employee'),
            ('manager', 'Manager'),
            ('hr', 'HR'),
        ],
        required=True,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500'
        })
    )
    
    class Meta:
        model = Employee
        fields = [
            'first_name', 'last_name', 'date_of_birth', 'phone', 'address',
            'department', 'job_title', 'salary', 'start_date', 'manager', 'status',
            'emergency_contact', 'emergency_phone',
            'annual_leave_balance', 'sick_leave_balance', 'vacation_balance',
            'notes',
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500',
                'placeholder': 'First name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500',
                'placeholder': 'Last name'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500',
                'placeholder': '(555) 123-4567'
            }),
            'address': forms.Textarea(attrs={
                'rows': 2,
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500',
                'placeholder': 'Street address, City, State, ZIP'
            }),
            'department': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500'
            }),
            'job_title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500',
                'placeholder': 'e.g., Software Engineer'
            }),
            'salary': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500',
                'placeholder': '50000.00'
            }),
            'start_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500'
            }),
            'manager': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500'
            }),
            'status': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500'
            }),
            'emergency_contact': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500',
                'placeholder': 'Emergency contact name'
            }),
            'emergency_phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500',
                'placeholder': '(555) 987-6543'
            }),
            'annual_leave_balance': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500',
                'step': '0.5'
            }),
            'sick_leave_balance': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500',
                'step': '0.5'
            }),
            'vacation_balance': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500',
                'step': '0.5'
            }),
            'notes': forms.Textarea(attrs={
                'rows': 3,
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500',
                'placeholder': 'Additional notes...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # If editing existing employee, populate email and role from user
        if self.instance and self.instance.pk and self.instance.user:
            self.fields['email'].initial = self.instance.user.email
            self.fields['role'].initial = self.instance.user.role
            self.fields['email'].widget.attrs['readonly'] = True
            self.fields['email'].widget.attrs['class'] += ' bg-gray-100'
    
    def clean_email(self):
        email = self.cleaned_data['email']
        
        # Check if email already exists (for new employees only)
        if not self.instance.pk:
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError('A user with this email already exists.')
        
        return email
    
    def save(self, commit=True):
        employee = super().save(commit=False)
    
        # If this is a new employee (no user yet)
        if not employee.pk or not employee.user_id:
            email = self.cleaned_data['email']
            role = self.cleaned_data['role']
        
            # Generate a random password
            random_password = secrets.token_urlsafe(12)
        
            # Generate employee ID
            last_employee = Employee.objects.order_by('-id').first()
            if last_employee:
                try:
                    last_num = int(last_employee.employee_id.replace('EMP', ''))
                    new_num = last_num + 1
                except (ValueError, AttributeError):
                    new_num = Employee.objects.count() + 1
            else:
                new_num = 1
            employee.employee_id = f"EMP{new_num:04d}"
        
            # Create the user account (NO USERNAME - your model doesn't use it!)
            user = User.objects.create_user(
                email=email,
                password=random_password,
                first_name=employee.first_name,
                last_name=employee.last_name,
            )
            user.role = role  # Set role after creation
            user.save()
        
            employee.user = user
        
            # Store password to show after creation
            self.generated_password = random_password
        
            print(f"✓ Created user: {user.email} (ID: {user.pk})")
            print(f"✓ Generated password: {random_password}")
        else:
            # Update existing user's role if changed
            if 'role' in self.cleaned_data and employee.user:
                employee.user.role = self.cleaned_data['role']
                employee.user.first_name = employee.first_name
                employee.user.last_name = employee.last_name
                employee.user.save()
                print(f"✓ Updated user: {employee.user.email}")
    
        if commit:
            employee.save()
            print(f"✓ Saved employee: {employee.employee_id} - {employee.full_name}")
    
        return employee


class EmployeeSearchForm(forms.Form):
    """Form for searching and filtering employees."""
    
    search = forms.CharField(
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500',
            'placeholder': 'Search by name, ID, or email...'
        })
    )
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        required=False,
        empty_label="All Departments",
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500'
        })
    )
    status = forms.ChoiceField(
        choices=[('', 'All Status')] + list(Employee.Status.choices),
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500'
        })
    )