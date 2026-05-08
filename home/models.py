from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    full_name = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    contact_no = models.CharField(max_length=20)
    cnic = models.CharField(max_length=20)
    property_id = models.IntegerField(null=True) # To know which house they wanted
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name
    
    
class PasswordResetOTP(models.Model):
    """
    Model to store OTP for password reset
    OTPs automatically expire after 60 seconds
    """
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    
    def save(self, *args, **kwargs):
        # Set expiration time to 60 seconds from creation
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(seconds=60)
        super().save(*args, **kwargs)
    
    def is_expired(self):
        """Check if OTP has expired"""
        return timezone.now() > self.expires_at
    
    def __str__(self):
        return f"OTP for {self.email} - Expires at {self.expires_at}"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Password Reset OTP"
        verbose_name_plural = "Password Reset OTPs"
 
# class PasswordResetTemp(models.Model):
#     email = models.EmailField(unique=True)
#     temp_password = models.CharField(max_length=255)
#     created_at = models.DateTimeField(auto_now_add=True)
#     expires_at = models.DateTimeField()
    
#     def save(self, *args, **kwargs):
#         if not self.expires_at:
#             self.expires_at = timezone.now() + timedelta(seconds=30)
#         super().save(*args, **kwargs)
    
#     def is_expired(self):
#         return timezone.now() > self.expires_at
    
#     def __str__(self):
#         return f"Temp password for {self.email} - Expires at {self.expires_at}"
    
#     class Meta:
#         ordering = ['-created_at']
#         verbose_name = "Temporary Password"
#         verbose_name_plural = "Temporary Passwords"
        
class Property(models.Model):
    STATUS_CHOICES = (
        ('Verified', 'Verified'),
        ('Unverified', 'Unverified'),
    )

    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    location = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    bedrooms = models.IntegerField()
    property_type = models.CharField(max_length=100)
    area = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(upload_to='properties/')
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Unverified')
    financing = models.BooleanField(default=True)

    def __str__(self):
        return self.title