from typing import Tuple

from django.contrib import admin

from bot.models import TelegramUser


# ----------------------------------------------------------------------------------------------------------------------
# Create admin models
@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    """Admin settings for TelegramUser"""
    list_display: Tuple[str, ...] = ('tg_username', 'user')
    readonly_fields: Tuple[str, ...] = ('tg_chat_id', 'tg_username', 'user', 'verification_code')
    search_fields: Tuple[str, ...] = ('user__username',)
    search_help_text: str = 'Поиск по пользователю'
