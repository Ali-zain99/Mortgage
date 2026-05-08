"""
Django management command to clean up expired OTPs
Run this command periodically (e.g., every minute via cron or celery)

Usage:
python manage.py cleanup_expired_otps
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from home.models import PasswordResetOTP


class Command(BaseCommand):
    help = 'Delete expired OTPs (older than 60 seconds)'

    def handle(self, *args, **options):
        now = timezone.now()
        
        # Delete expired OTPs
        expired_otps = PasswordResetOTP.objects.filter(expires_at__lt=now)
        otp_count = expired_otps.count()
        expired_otps.delete()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully deleted {otp_count} expired OTPs'
            )
        )