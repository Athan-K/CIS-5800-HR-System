"""
Management command to generate sample data for Ethos HRMS.
"""

import random
from datetime import date, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.employees.models import Department, Employee, Attendance, Payslip, LeaveRequest

User = get_user_model()


class Command(BaseCommand):
    help = 'Generate sample data for Ethos HRMS'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Create Departments
        departments_data = [
            ('Human Resources', 'Manages employee relations and recruitment'),
            ('Engineering', 'Software development and technical operations'),
            ('Sales', 'Revenue generation and client relationships'),
            ('Marketing', 'Brand management and promotional activities'),
            ('Finance', 'Financial planning and accounting'),
            ('Operations', 'Day-to-day business operations'),
        ]
        
        departments = []
        for name, desc in departments_data:
            dept, created = Department.objects.get_or_create(
                name=name,
                defaults={'description': desc}
            )
            departments.append(dept)
            if created:
                self.stdout.write(f'  Created department: {name}')
        
        # Sample employee data
        employees_data = [
            ('John', 'Smith', 'HR Manager', 'hr', 85000),
            ('Sarah', 'Johnson', 'HR Specialist', 'hr', 55000),
            ('Michael', 'Williams', 'Software Engineer', 'employee', 95000),
            ('Emily', 'Brown', 'Senior Developer', 'employee', 110000),
            ('David', 'Jones', 'Sales Manager', 'manager', 90000),
            ('Jessica', 'Garcia', 'Sales Representative', 'employee', 60000),
            ('Christopher', 'Miller', 'Marketing Director', 'manager', 95000),
            ('Ashley', 'Davis', 'Marketing Coordinator', 'employee', 50000),
            ('Matthew', 'Rodriguez', 'Financial Analyst', 'employee', 75000),
            ('Amanda', 'Martinez', 'Accountant', 'employee', 65000),
            ('Daniel', 'Hernandez', 'Operations Manager', 'manager', 80000),
            ('Stephanie', 'Lopez', 'Operations Coordinator', 'employee', 48000),
            ('Andrew', 'Gonzalez', 'DevOps Engineer', 'employee', 100000),
            ('Nicole', 'Wilson', 'UX Designer', 'employee', 85000),
            ('Joshua', 'Anderson', 'Product Manager', 'manager', 105000),
            ('Samantha', 'Thomas', 'QA Engineer', 'employee', 70000),
            ('Ryan', 'Taylor', 'Data Analyst', 'employee', 72000),
            ('Elizabeth', 'Moore', 'Customer Success', 'employee', 55000),
            ('Brandon', 'Jackson', 'Technical Writer', 'employee', 60000),
            ('Megan', 'Martin', 'Recruiter', 'employee', 52000),
            ('Justin', 'Lee', 'Backend Developer', 'employee', 92000),
            ('Rachel', 'Perez', 'Frontend Developer', 'employee', 88000),
            ('Kevin', 'Thompson', 'Sales Representative', 'employee', 58000),
            ('Lauren', 'White', 'Marketing Specialist', 'employee', 54000),
            ('Tyler', 'Harris', 'Support Specialist', 'employee', 45000),
            ('Kayla', 'Sanchez', 'Office Manager', 'employee', 50000),
            ('Jacob', 'Clark', 'Security Engineer', 'employee', 98000),
            ('Brittany', 'Ramirez', 'Business Analyst', 'employee', 78000),
            ('Nathan', 'Lewis', 'Project Manager', 'manager', 88000),
            ('Amber', 'Robinson', 'Graphic Designer', 'employee', 62000),
            ('Adam', 'Walker', 'Systems Administrator', 'employee', 82000),
            ('Danielle', 'Young', 'Content Writer', 'employee', 48000),
            ('Eric', 'Allen', 'Mobile Developer', 'employee', 94000),
            ('Victoria', 'King', 'HR Assistant', 'employee', 42000),
            ('Sean', 'Wright', 'Network Engineer', 'employee', 86000),
            ('Christina', 'Scott', 'Executive Assistant', 'employee', 52000),
            ('Patrick', 'Torres', 'Sales Director', 'manager', 115000),
            ('Michelle', 'Nguyen', 'Software Architect', 'employee', 130000),
            ('Derek', 'Hill', 'Database Administrator', 'employee', 88000),
            ('Heather', 'Flores', 'Training Coordinator', 'employee', 50000),
            ('Brian', 'Green', 'IT Support', 'employee', 55000),
            ('Melissa', 'Adams', 'Payroll Specialist', 'employee', 52000),
            ('Steven', 'Nelson', 'Quality Manager', 'manager', 82000),
            ('Rebecca', 'Baker', 'Legal Counsel', 'employee', 120000),
            ('Timothy', 'Hall', 'Facilities Manager', 'employee', 58000),
            ('Laura', 'Rivera', 'Social Media Manager', 'employee', 54000),
            ('Jeffrey', 'Campbell', 'Research Analyst', 'employee', 68000),
            ('Angela', 'Mitchell', 'Customer Service Rep', 'employee', 42000),
            ('Jason', 'Carter', 'Warehouse Supervisor', 'employee', 48000),
            ('Kelly', 'Roberts', 'Benefits Coordinator', 'employee', 50000),
        ]
        
        dept_assignments = {
            'HR': ['Human Resources'],
            'Engineering': ['Engineering'],
            'Sales': ['Sales'],
            'Marketing': ['Marketing'],
            'Finance': ['Finance'],
            'Operations': ['Operations'],
        }
        
        job_to_dept = {
            'HR Manager': 'Human Resources',
            'HR Specialist': 'Human Resources',
            'HR Assistant': 'Human Resources',
            'Recruiter': 'Human Resources',
            'Benefits Coordinator': 'Human Resources',
            'Payroll Specialist': 'Human Resources',
            'Training Coordinator': 'Human Resources',
            'Software Engineer': 'Engineering',
            'Senior Developer': 'Engineering',
            'DevOps Engineer': 'Engineering',
            'Backend Developer': 'Engineering',
            'Frontend Developer': 'Engineering',
            'Mobile Developer': 'Engineering',
            'Software Architect': 'Engineering',
            'QA Engineer': 'Engineering',
            'Security Engineer': 'Engineering',
            'Database Administrator': 'Engineering',
            'Systems Administrator': 'Engineering',
            'Network Engineer': 'Engineering',
            'IT Support': 'Engineering',
            'Sales Manager': 'Sales',
            'Sales Representative': 'Sales',
            'Sales Director': 'Sales',
            'Customer Success': 'Sales',
            'Customer Service Rep': 'Sales',
            'Marketing Director': 'Marketing',
            'Marketing Coordinator': 'Marketing',
            'Marketing Specialist': 'Marketing',
            'UX Designer': 'Marketing',
            'Graphic Designer': 'Marketing',
            'Content Writer': 'Marketing',
            'Social Media Manager': 'Marketing',
            'Technical Writer': 'Marketing',
            'Financial Analyst': 'Finance',
            'Accountant': 'Finance',
            'Business Analyst': 'Finance',
            'Legal Counsel': 'Finance',
            'Research Analyst': 'Finance',
            'Operations Manager': 'Operations',
            'Operations Coordinator': 'Operations',
            'Product Manager': 'Operations',
            'Project Manager': 'Operations',
            'Data Analyst': 'Operations',
            'Office Manager': 'Operations',
            'Executive Assistant': 'Operations',
            'Facilities Manager': 'Operations',
            'Quality Manager': 'Operations',
            'Support Specialist': 'Operations',
            'Warehouse Supervisor': 'Operations',
        }
        
        created_employees = []
        
        for i, (first, last, title, role, salary) in enumerate(employees_data):
            email = f"{first.lower()}.{last.lower()}@ethos.com"
            employee_id = f"ETH{str(i+1001).zfill(4)}"
            
            # Check if user already exists
            if User.objects.filter(email=email).exists():
                self.stdout.write(f'  Skipping {email} (already exists)')
                continue
            
            # Create user
            user = User.objects.create_user(
                email=email,
                password='password123',
                role=role,
            )
            
            # Get department
            dept_name = job_to_dept.get(title, 'Operations')
            dept = Department.objects.get(name=dept_name)
            
            # Random start date within last 5 years
            days_ago = random.randint(30, 1825)
            start_date = date.today() - timedelta(days=days_ago)
            
            # Create employee
            employee = Employee.objects.create(
                user=user,
                employee_id=employee_id,
                first_name=first,
                last_name=last,
                department=dept,
                job_title=title,
                start_date=start_date,
                status='active',
                salary=Decimal(str(salary)),
                phone=f"555-{random.randint(100,999)}-{random.randint(1000,9999)}",
                address=f"{random.randint(100,9999)} Main Street, Anytown, ST {random.randint(10000,99999)}",
                emergency_contact=f"Emergency Contact for {first}",
                emergency_phone=f"555-{random.randint(100,999)}-{random.randint(1000,9999)}",
                annual_leave_balance=Decimal(str(random.randint(5, 20))),
                sick_leave_balance=Decimal(str(random.randint(3, 10))),
                vacation_balance=Decimal(str(random.randint(5, 15))),
            )
            created_employees.append(employee)
            self.stdout.write(f'  Created employee: {first} {last}')
        
        # Create some attendance records for the last 30 days
        self.stdout.write('Creating attendance records...')
        for employee in Employee.objects.all()[:20]:  # First 20 employees
            for days_ago in range(1, 31):
                record_date = date.today() - timedelta(days=days_ago)
                # Skip weekends
                if record_date.weekday() >= 5:
                    continue
                
                # Random attendance status
                status_choices = ['present'] * 8 + ['late'] * 1 + ['absent'] * 1
                status = random.choice(status_choices)
                
                if status == 'present':
                    time_in = f"0{random.randint(8,9)}:{random.randint(0,59):02d}:00"
                    time_out = f"{random.randint(17,18)}:{random.randint(0,59):02d}:00"
                    hours = Decimal(str(round(random.uniform(7.5, 9.0), 2)))
                elif status == 'late':
                    time_in = f"{random.randint(9,10)}:{random.randint(0,59):02d}:00"
                    time_out = f"{random.randint(17,19)}:{random.randint(0,59):02d}:00"
                    hours = Decimal(str(round(random.uniform(6.5, 8.0), 2)))
                else:
                    time_in = None
                    time_out = None
                    hours = Decimal('0')
                
                Attendance.objects.get_or_create(
                    employee=employee,
                    date=record_date,
                    defaults={
                        'time_in': time_in,
                        'time_out': time_out,
                        'hours_worked': hours,
                        'status': status,
                    }
                )
        
        # Create some payslips
        self.stdout.write('Creating payslips...')
        for employee in Employee.objects.all():
            for month_ago in range(1, 4):  # Last 3 months
                pay_date = date.today().replace(day=15) - timedelta(days=month_ago*30)
                period_start = pay_date.replace(day=1)
                period_end = pay_date.replace(day=28)
                
                gross = employee.salary / 12
                deductions = gross * Decimal('0.25')  # 25% deductions
                net = gross - deductions
                
                Payslip.objects.get_or_create(
                    employee=employee,
                    pay_period_start=period_start,
                    pay_period_end=period_end,
                    defaults={
                        'pay_date': pay_date,
                        'gross_pay': gross,
                        'deductions': deductions,
                        'net_pay': net,
                    }
                )
        
        # Create some leave requests
        self.stdout.write('Creating leave requests...')
        statuses = ['pending', 'approved', 'approved', 'approved', 'rejected']
        leave_types = ['annual', 'sick', 'vacation']
        
        for employee in random.sample(list(Employee.objects.all()), 15):
            start = date.today() + timedelta(days=random.randint(-30, 60))
            end = start + timedelta(days=random.randint(1, 5))
            
            LeaveRequest.objects.create(
                employee=employee,
                leave_type=random.choice(leave_types),
                start_date=start,
                end_date=end,
                reason=f"Personal time off request",
                status=random.choice(statuses),
            )
        
        self.stdout.write(self.style.SUCCESS('\nSample data created successfully!'))
        self.stdout.write(f'\nCreated:')
        self.stdout.write(f'  - {Department.objects.count()} departments')
        self.stdout.write(f'  - {Employee.objects.count()} employees')
        self.stdout.write(f'  - {Attendance.objects.count()} attendance records')
        self.stdout.write(f'  - {Payslip.objects.count()} payslips')
        self.stdout.write(f'  - {LeaveRequest.objects.count()} leave requests')
        self.stdout.write(f'\nAll employees have password: password123')