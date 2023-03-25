from django.apps import AppConfig


class CoreConfig(AppConfig):
    """Configuration class for the Core app"""
    default_auto_field: str = 'django.db.models.BigAutoField'
    name: str = 'core'
