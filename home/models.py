from django.db import models
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
    
# class Property(models.Model):
#     title = models.CharField(max_length=255)
#     location = models.CharField(max_length=255)
#     price = models.DecimalField(max_digits=12, decimal_places=2)   # or however you store price
#     bedrooms = models.IntegerField(default=0)
#     type = models.CharField(max_length=100, blank=True)
#     image = models.ImageField(upload_to='properties/', blank=True, null=True)
#     status = models.CharField(max_length=50, default='Pending')
#     description = models.TextField(blank=True)
    # add any other fields you need
    
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