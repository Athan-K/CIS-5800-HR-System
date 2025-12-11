from django.core.management.base import BaseCommand
from apps.accounts.models import User
import os


class Command(BaseCommand):
    help = 'Creates a default admin user if none exists'

    def handle(self, *args, **options):
        admin_email = os.environ.get('ADMIN_EMAIL', 'admin@ethos.com')
        admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123456')
        
        if not User.objects.filter(email=admin_email).exists():
            User.objects.create_superuser(
                email=admin_email,
                password=admin_password,
            )
            self.stdout.write(self.style.SUCCESS(f'Admin user created: {admin_email}'))
        else:
            self.stdout.write(self.style.WARNING(f'Admin user already exists: {admin_email}'))