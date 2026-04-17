from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    # This determines which columns show up in the list view
    list_display = ('user', 'city', 'contact_no', 'cnic')
    search_fields = ('user__username', 'cnic', 'city')