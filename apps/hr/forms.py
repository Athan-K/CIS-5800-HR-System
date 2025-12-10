"""
Forms for HR management.
"""

from django import forms
from django.contrib.auth import get_user_model
from apps.employees.models import Employee, Department

User = get_user_model()


class EmployeeForm(forms.ModelForm):
    """Form for creating/editing employees."""
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500',
        })
    )
    
    class Meta:
        model = Employee
        fields = [
            'employee_id', 'first_name', 'last_name', 'department',
            'job_title', 'manager', 'start_date', 'status', 'salary',
            'phone', 'address', 'emergency_contact', 'emergency_phone',
            'annual_leave_balance', 'sick_leave_balance', 'vacation_balance',
            'notes'
        ]
        widgets = {
            'employee_id': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500',
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500',
            }),
            'department': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500',
            }),
            'job_title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500',
            }),
            'manager': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500',
            }),
            'start_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500',
            }),
            'status': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500',
            }),
            'salary': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500',
                'step': '0.01',
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500',
            }),
            'address': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500',
                'rows': 3,
            }),
            'emergency_contact': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500',
            }),
            'emergency_phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500',
            }),
            'annual_leave_balance': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500',
                'step': '0.5',
            }),
            'sick_leave_balance': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500',
                'step': '0.5',
            }),
            'vacation_balance': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500',
                'step': '0.5',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500',
                'rows': 4,
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['email'].initial = self.instance.user.email
    
    def save(self, commit=True):
        employee = super().save(commit=False)
    
        if not employee.pk:
        # Creating new employee - also create user account
            from django.contrib.auth.hashers import make_password
            import secrets
        
        # Generate a random password
            random_password = secrets.token_urlsafe(12)
        
            user = User.objects.create_user(
                email=self.cleaned_data['email'],
                password=random_password,
            )
            employee.user = user
        
            # TODO: Send email with temporary password
            print(f"New user created with temporary password: {random_password}")
        else:
        # Updating - update email if changed
            employee.user.email = self.cleaned_data['email']
            employee.user.save()
    
        if commit:
            employee.save()
    
        return employee


class EmployeeSearchForm(forms.Form):
    """Search form for employee list."""
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg',
            'placeholder': 'Search by name, ID, or email...',
        })
    )
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        required=False,
        empty_label='All Departments',
        widget=forms.Select(attrs={
            'class': 'px-4 py-2 border border-gray-300 rounded-lg',
        })
    )
    status = forms.ChoiceField(
        choices=[('', 'All Status')] + list(Employee.Status.choices),
        required=False,
        widget=forms.Select(attrs={
            'class': 'px-4 py-2 border border-gray-300 rounded-lg',
        })
    )