from typing import Optional, Tuple, Dict

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from core.models import User


# ----------------------------------------------------------------------------------------------------------------------
# Create models
class CustomAdmin(UserAdmin):
    """Custom settings for admin panel"""

    fieldsets: Tuple[Tuple[Optional[str], Dict[str, Tuple[str, ...]]], ...] = (  # type: ignore
        (None, {"fields": ("username",)}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    readonly_fields: tuple[str, ...] = ("last_login", "date_joined")


# ----------------------------------------------------------------------------------------------------------------------
# Register models
admin.site.register(User, CustomAdmin)
