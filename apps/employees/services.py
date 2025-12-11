from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from .models import Notification
import logging

logger = logging.getLogger(__name__)


def create_notification(recipient, notification_type, title, message, link=''):
    """Create an in-app notification."""
    return Notification.objects.create(
        recipient=recipient,
        notification_type=notification_type,
        title=title,
        message=message,
        link=link
    )


def send_email_notification(to_email, subject, template_name, context):
    """Send an email notification."""
    try:
        html_content = render_to_string(template_name, context)
        text_content = strip_tags(html_content)
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)
        
        logger.info(f"Email sent to {to_email}: {subject}")
        return True
    except Exception as e:
        logger.error(f"Email failed to {to_email}: {str(e)}")
        return False


def notify_leave_approved(leave_request):
    """Notify employee that their leave request was approved."""
    employee = leave_request.employee
    
    create_notification(
        recipient=employee,
        notification_type=Notification.Type.LEAVE_APPROVED,
        title='Leave Request Approved',
        message=f'Your {leave_request.get_leave_type_display()} request for {leave_request.start_date.strftime("%b %d")} - {leave_request.end_date.strftime("%b %d, %Y")} has been approved.',
        link='/employee/leave/'
    )
    
    send_email_notification(
        to_email=employee.user.email,
        subject='Leave Request Approved - Ethos HRMS',
        template_name='emails/leave_approved.html',
        context={'employee': employee, 'leave_request': leave_request}
    )


def notify_leave_rejected(leave_request):
    """Notify employee that their leave request was rejected."""
    employee = leave_request.employee
    
    create_notification(
        recipient=employee,
        notification_type=Notification.Type.LEAVE_REJECTED,
        title='Leave Request Rejected',
        message=f'Your {leave_request.get_leave_type_display()} request for {leave_request.start_date.strftime("%b %d")} - {leave_request.end_date.strftime("%b %d, %Y")} has been rejected.',
        link='/employee/leave/'
    )
    
    send_email_notification(
        to_email=employee.user.email,
        subject='Leave Request Update - Ethos HRMS',
        template_name='emails/leave_rejected.html',
        context={'employee': employee, 'leave_request': leave_request}
    )


def notify_correction_approved(correction):
    """Notify employee that their attendance correction was approved."""
    employee = correction.employee
    
    create_notification(
        recipient=employee,
        notification_type=Notification.Type.CORRECTION_APPROVED,
        title='Attendance Correction Approved',
        message=f'Your attendance correction request for {correction.date.strftime("%b %d, %Y")} has been approved.',
        link='/employee/attendance/'
    )
    
    send_email_notification(
        to_email=employee.user.email,
        subject='Attendance Correction Approved - Ethos HRMS',
        template_name='emails/correction_approved.html',
        context={'employee': employee, 'correction': correction}
    )


def notify_correction_rejected(correction):
    """Notify employee that their attendance correction was rejected."""
    employee = correction.employee
    
    create_notification(
        recipient=employee,
        notification_type=Notification.Type.CORRECTION_REJECTED,
        title='Attendance Correction Rejected',
        message=f'Your attendance correction request for {correction.date.strftime("%b %d, %Y")} has been rejected.',
        link='/employee/attendance/'
    )
    
    send_email_notification(
        to_email=employee.user.email,
        subject='Attendance Correction Update - Ethos HRMS',
        template_name='emails/correction_rejected.html',
        context={'employee': employee, 'correction': correction}
    )

def send_welcome_email(employee, password):
    """Send welcome email with login credentials to new employee."""
    send_email_notification(
        to_email=employee.user.email,
        subject='Welcome to Ethos HRMS - Your Account Details',
        template_name='emails/welcome.html',
        context={
            'employee': employee,
            'password': password,
            'login_url': 'http://127.0.0.1:8000/accounts/login/'
        }
    )