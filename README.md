# Ethos HRMS

A modern Human Resource Management System built with Django for Ethos Manufacturing.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Django](https://img.shields.io/badge/Django-5.1-green)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.0-38B2AC)

## 📋 Overview

Ethos HRMS is a full-featured human resource management system designed to streamline HR operations. It provides separate portals for HR administrators and employees, enabling efficient management of employee data, leave requests, attendance tracking, and more.

## ✨ Features

### HR Portal
- **Dashboard** - Overview of key HR metrics and pending tasks
- **Employee Management** - Add, edit, view, and manage employee profiles
- **Department Management** - Organize employees by departments
- **Leave Management** - Review and approve/reject leave requests
- **Attendance Corrections** - Handle employee attendance correction requests
- **Reports & Analytics** - Generate headcount, department, leave, and attendance reports
- **Audit Log** - Track all system changes for compliance

### Employee Portal
- **Dashboard** - Personal overview with attendance calendar
- **My Profile** - View personal and employment information
- **Leave Requests** - Submit and track leave requests
- **Attendance** - View attendance records and request corrections
- **Notifications** - Receive updates on leave approvals, rejections, etc.

### Security Features
- **Two-Factor Authentication (2FA)** - Optional TOTP-based 2FA using authenticator apps
- **Role-Based Access Control** - Admin, HR, Manager, and Employee roles
- **Terminated Employee Blocking** - Automatic access revocation for terminated employees

### Email Notifications
- Welcome emails with login credentials for new employees
- Leave request approval/rejection notifications
- Attendance correction notifications
- Password reset emails

## 🛠️ Tech Stack

- **Backend**: Django 5.1, Python 3.11
- **Frontend**: Tailwind CSS, HTMX
- **Database**: PostgreSQL (production), SQLite (development)
- **Authentication**: Django Allauth, Django OTP
- **Email**: SendGrid API
- **Charts**: Chart.js
- **Deployment**: Render

## 📦 Installation

### Prerequisites
- Python 3.11+
- pip
- Git

### Local Setup

1. **Clone the repository**
```bash
   git clone https://github.com/yourusername/CIS-5800-HR-System.git
   cd CIS-5800-HR-System
```

2. **Create a virtual environment**
```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
```

3. **Install dependencies**
```bash
   pip install -r requirements.txt
```

4. **Create a `.env` file** in the project root:
```env
   DEBUG=True
   SECRET_KEY=your-secret-key-here
   
   # Email (SendGrid)
   SENDGRID_API_KEY=your-sendgrid-api-key
   SENDGRID_FROM_EMAIL=your-verified-email@example.com
   BASE_URL=http://127.0.0.1:8000
```

5. **Run migrations**
```bash
   python manage.py migrate
```

6. **Create a superuser (optional)**
```bash
   python manage.py createsuperuser
```

7. **Seed sample data (optional)**
```bash
   python manage.py seed_data
```

8. **Run the development server**
```bash
   python manage.py runserver
```

9. **Access the application**
   - Open http://127.0.0.1:8000 in your browser
   - Default admin login: `admin@ethos.com` / `admin123`


## 🔧 Configuration

### SendGrid Setup
1. Create a SendGrid account at [sendgrid.com](https://sendgrid.com)
2. Verify your sender email under Settings → Sender Authentication
3. Create an API key under Settings → API Keys
4. Add the API key to your environment variables

### Two-Factor Authentication
- Employees can enable 2FA in Settings
- Uses TOTP (Time-based One-Time Password)
- Compatible with Google Authenticator, Authy, 

## 👨‍💻 Contributors

- Team 2 - CIS 5800
