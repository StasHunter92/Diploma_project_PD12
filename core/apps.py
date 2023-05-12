from django.apps import AppConfig


# ----------------------------------------------------------------------------------------------------------------------
# Create configuration
class CoreConfig(AppConfig):
    """Configuration class for the Core app"""

    default_auto_field: str = "django.db.models.BigAutoField"
    name: str = "core"
