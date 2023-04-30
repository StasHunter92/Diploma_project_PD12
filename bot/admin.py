from django.contrib import admin

from bot.models import TelegramUser


# ----------------------------------------------------------------------------------------------------------------------
# Create admin models
@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    """Admin settings for TelegramUser"""
    list_display: tuple[str] = ('tg_username', 'user')
    readonly_fields: tuple[str] = ('tg_chat_id', 'tg_username', 'user', 'verification_code')
    search_fields: tuple[str] = ('user__username',)
    search_help_text: str = 'Поиск по пользователю'
