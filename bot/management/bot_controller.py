import json
import secrets
import datetime
from typing import Optional

from django.db.models import QuerySet

from bot.tg.client import TgClient
from bot.tg.dc import Message, GetUpdatesResponse
from bot.models import TelegramUser
from goals.models.goal import Goal
from diploma_project_pd12.settings import RANDOM_STRING_CHARS
from goals.models.goal_category import GoalCategory


# ----------------------------------------------------------------------------------------------------------------------
class Controller(object):
    """
    Controller for the database manipulation
    and additional functionality
    """

    @classmethod
    def get_telegram_user(cls, chat_id: int) -> Optional[TelegramUser]:
        """
        Get TelegramUser object from the database

        Args:
            chat_id: User chat id from Telegram

        Returns:
            TelegramUser object if found otherwise None
        """
        try:
            user: TelegramUser = TelegramUser.objects.get(tg_chat_id=chat_id)
        except TelegramUser.DoesNotExist:
            return None

        return user

    # ----------------------------------------------------------------
    @classmethod
    def create_telegram_user(cls, client: TgClient, message: Message) -> None:
        """
        Creates a new user and sends greeting message with verification code

        Args:
            client: TelegramClient instance
            message: The message object containing user information

        Returns:
            None
        """
        verification_code: str = cls.create_verification_code()
        username: str = (
            message.from_.username if message.from_.username else "Anonymous"
        )

        TelegramUser.objects.create(
            tg_chat_id=message.chat.id,
            tg_username=username,
            verification_code=verification_code,
        )

        keyboard: list[list[str]] = [["/confirm"]]
        reply_markup: str = json.dumps({
            "keyboard": keyboard,
            "resize_keyboard": True,
            "one_time_keyboard": False,
            "is_persistent": True,
        })

        client.send_message(
            chat_id=message.chat.id,
            text=f"Добро пожаловать, {message.from_.username}! \n"
            f"Ваш одноразовый код авторизации: {verification_code} \n",
            reply_markup=reply_markup,
        )

    # ----------------------------------------------------------------
    @classmethod
    def create_verification_code(
        cls, length: int = 6, allowed_chars: str = RANDOM_STRING_CHARS
    ) -> str:
        """
        Creates verification code

        Args:
            length: Code length
            allowed_chars: String with allowed chars

        Returns:
            String with random generated verification code
        """
        return "".join(secrets.choice(allowed_chars) for _ in range(length))

    # ----------------------------------------------------------------
    @classmethod
    def update_verification_code(cls, client: TgClient, user: TelegramUser) -> None:
        """
        Updates 'verification_code' field in user object and sends it to the chat

        Args:
            client: TelegramClient instance
            user: TelegramUser object

        Returns:
            None
        """
        user.verification_code = cls.create_verification_code()
        user.save(update_fields=("verification_code",))

        client.send_message(
            chat_id=user.tg_chat_id,
            text=f"Вы еще не подтвердили код в приложении \n"
            f"Ваш новый одноразовый код авторизации: {user.verification_code} \n",
        )

    # ----------------------------------------------------------------
    @classmethod
    def update_order(cls, client: TgClient, offset: int) -> GetUpdatesResponse:
        """
        Fetches updates from Telegram server

        Args:
            client: TelegramClient instance
            offset: The offset of the last update that the bot has processed

        Returns:
            GetUpdatesResponse: A response object that holds information
            about the updates returned by the API
        """
        return client.get_updates(offset=offset)

    # ----------------------------------------------------------------
    @classmethod
    def get_goals(cls, user: TelegramUser) -> QuerySet[Goal]:
        """
        Get goals from the database

        Args:
            user: TelegramUser object

        Returns:
            QuerySet[Goal]: List of goals returned by the API
        """
        # Return a queryset of goals the user is a participant of
        return (
            Goal.objects.select_related("category")
            .filter(
                category__board__participants__user=user.user,
                category__board__is_deleted=False,
                category__is_deleted=False,
            )
            .exclude(status=Goal.Status.archived)
        )

    # ----------------------------------------------------------------
    @classmethod
    def get_categories(cls, user: TelegramUser) -> QuerySet[GoalCategory]:
        """
        Get categories from the database

        Args:
            user: TelegramUser object

        Returns:
            QuerySet[GoalCategory]: List of categories returned by the API
        """
        return GoalCategory.objects.select_related("board").filter(
            board__participants__role__in=[1, 2],
            board__participants__user=user.user,
            board__is_deleted=False,
            is_deleted=False,
        )

    # ----------------------------------------------------------------
    @classmethod
    def get_category(
        cls, user: TelegramUser, message: Message
    ) -> Optional[GoalCategory]:
        """
        Get category from the database

        Args:
            user: TelegramUser object
            message: The message object containing user information

        Returns:
            Optional[GoalCategory]: A single category object returned by the API
        """
        return (
            GoalCategory.objects.select_related("board")
            .filter(
                board__participants__role__in=[1, 2],
                title=message.text,
                board__participants__user=user.user,
                board__is_deleted=False,
                is_deleted=False,
            )
            .first()
        )

    # ----------------------------------------------------------------
    @classmethod
    def create_goal(
        cls, user: TelegramUser, message: Message, category: GoalCategory, days: int
    ) -> Goal:
        """
        Creates a new goal

        Args:
            user: TelegramUser object
            message: The message object containing user information
            category: GoalCategory object
            days: Delta for the due date of the goal

        Returns:
            Goal: A single created goal object
        """
        due_date: datetime.date = datetime.date.today() + datetime.timedelta(days=days)
        return Goal.objects.create(
            user=user.user,
            category=category,
            title=message.text,
            due_date=due_date.strftime("%Y-%m-%d"),
        )  # type: ignore
