from django.db import models

from core.models import User


# ----------------------------------------------------------------------------------------------------------------------
# Create models
class TelegramUser(models.Model):
    """TelegramUser model"""
    tg_chat_id = models.PositiveBigIntegerField(verbose_name='ID чата', unique=True)
    tg_username = models.CharField(max_length=50, verbose_name='Никнейм пользователя', null=True)
    user = models.ForeignKey(User, verbose_name='Пользователь', null=True, on_delete=models.CASCADE)
    verification_code = models.CharField(max_length=6, verbose_name='Код авторизации', null=True)

    class Meta:
        verbose_name: str = 'Telegram аккаунт'
        verbose_name_plural: str = 'Telegram аккаунты'

    def __str__(self):
        """Returns the username"""
        return self.tg_username
