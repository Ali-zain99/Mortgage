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