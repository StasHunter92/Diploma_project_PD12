from django.contrib.auth.models import AbstractUser


# from django.db import models


# Create your models here.
class User(AbstractUser):
    class Meta:
        """
        Meta information for user model
        """
        verbose_name: str = 'Пользователь'
        verbose_name_plural: str = 'Пользователи'
