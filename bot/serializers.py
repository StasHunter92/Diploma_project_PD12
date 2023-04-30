from rest_framework import serializers

from bot.models import TelegramUser
from bot.tg.client import TgClient
from diploma_project_pd12.settings import env


# ----------------------------------------------------------------------------------------------------------------------
# Create serializers
class TelegramUserVerificationSerializer(serializers.ModelSerializer):
    """
    Serializer for verifying a Telegram user's identity
    and linking their account to their Telegram account
    """
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = TelegramUser
        fields = '__all__'
        read_only_fields = ['tg_chat_id', 'tg_username', 'verification_code']

    def update(self, telegram_user: TelegramUser, validated_data: dict) -> TelegramUser:
        """
        Updates the given 'telegram_user' object with the 'validated_data' and saves it to the database

        Args:
            telegram_user: The 'TelegramUser' object to update
            validated_data: The validated data to update the 'telegram_user' object with

        Returns:
            The updated 'telegram_user' object
        """
        telegram_user.user = validated_data['user']
        telegram_user.save(update_fields=('user',))

        # Send a success message to the user's Telegram chat
        TgClient(env('TG_TOKEN')).send_message(
            chat_id=telegram_user.tg_chat_id,
            text='Вы успешно авторизовались в боте!'
        )

        return telegram_user
