import requests
from requests import Response

from bot.tg.dc import GetUpdatesResponseSchema, SendMessageResponseSchema, GetUpdatesResponse, SendMessageResponse


# ----------------------------------------------------------------------------------------------------------------------
# Create client
class TgClient:

    def __init__(self, token: str) -> None:
        self.token = token

    def get_url(self, method: str) -> str:
        """Returns the url depending on the request method"""
        return f"https://api.telegram.org/bot{self.token}/{method}"

    def get_updates(self, offset: int = 0, timeout: int = 10) -> GetUpdatesResponse:
        """
        Sends a GET request to the Telegram API to retrieve updates for the bot

        Args:
            offset: The update identifier to start from. Defaults to 0
            timeout: The maximum amount of time to wait for updates, in seconds. Defaults to 10

        Return:
            GetUpdatesResponse: A response object that holds information about the updates returned by the API
        """
        url: str = self.get_url("getUpdates")
        response: Response = requests.get(
            url=url, params={"offset": offset, "timeout": timeout}
        )
        data = response.json()
        return GetUpdatesResponseSchema().load(data)

    def send_message(
        self, chat_id: int, text: str, reply_markup=None, parse_mode=None
    ) -> SendMessageResponse:
        """
        Sends a message to a specified chat

        Args:
            chat_id: Unique identifier for the target chat
            text: Text of the message to be sent
            reply_markup: JSON-serialized object for an inline keyboard or custom reply keyboard
            parse_mode: Mode for parsing entities in the message text

        Return:
            SendMessageResponse: A response object containing information about the message
        """
        url: str = self.get_url("sendMessage")
        response: Response = requests.get(
            url=url,
            params={
                "chat_id": chat_id,
                "text": text,
                "reply_markup": reply_markup,
                "parse_mode": parse_mode,
            },
        )
        data = response.json()
        return SendMessageResponseSchema().load(data)
