from django.apps import AppConfig


# ----------------------------------------------------------------------------------------------------------------------
# Create configuration
class BotConfig(AppConfig):
    """Configuration class for the Bot app"""

    default_auto_field: str = "django.db.models.BigAutoField"
    name: str = "bot"
