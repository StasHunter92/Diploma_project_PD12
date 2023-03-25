from django.contrib.auth.models import AbstractUser


# ----------------------------------------------------------------------------------------------------------------------
# Create models
class User(AbstractUser):
    """Custom User model with verbose names for admin interface"""

    class Meta:
        """Meta information for user model"""
        verbose_name: str = 'Пользователь'
        verbose_name_plural: str = 'Пользователи'
