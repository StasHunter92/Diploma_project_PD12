from django.apps import AppConfig


# ----------------------------------------------------------------------------------------------------------------------
# Create configuration
class GoalsConfig(AppConfig):
    """Configuration class for the Goal app"""
    default_auto_field: str = 'django.db.models.BigAutoField'
    name: str = 'goals'
