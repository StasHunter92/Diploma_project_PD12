from typing import Any

from rest_framework.generics import UpdateAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer

from bot.models import TelegramUser
from bot.serializers import TelegramUserVerificationSerializer
from core.models import User


# ----------------------------------------------------------------------------------------------------------------------
# Create views
class TelegramUserVerificationView(UpdateAPIView):
    """
    View for verifying a Telegram user's identity and linking their account to their Telegram account
    """
    serializer_class = TelegramUserVerificationSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self) -> TelegramUser:
        """
        Retrieve the 'TelegramUser' object with the verification code specified in the request data

        Returns:
            TelegramUser: The 'TelegramUser' object with the specified verification code

        Raises:
            Http404: If a 'TelegramUser' object with the specified verification code does not exist
        """
        return get_object_or_404(TelegramUser, verification_code=self.request.data.get('verification_code'))

    def patch(self, request: Request, *args, **kwargs) -> Response:
        """
        Handle the PATCH request to verify the user's identity and link their account to their Telegram account

        Args:
            request: The HTTP request object

        Returns:
            Response: A response containing the serialized data of the updated 'TelegramUser' object
        """
        user: User = request.user  # type: ignore
        telegram_user: TelegramUser = self.get_object()
        serializer: BaseSerializer[Any] = self.get_serializer(
            instance=telegram_user,
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(user=user)

        return Response(serializer.data)
