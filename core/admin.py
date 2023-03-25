from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from core.models import User


# ----------------------------------------------------------------------------------------------------------------------
# Create models
class CustomAdmin(UserAdmin):
    """Custom settings for admin panel"""
    exclude: tuple[str] = ('password',)
    readonly_fields: tuple[str] = ('date_joined', 'last_login')


# ----------------------------------------------------------------------------------------------------------------------
# Register models
admin.site.register(User, CustomAdmin)
