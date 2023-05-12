import json
import logging
from typing import Optional

from django.db.models import QuerySet
from transitions import Machine

from bot.management.bot_controller import Controller
from bot.tg.client import TgClient
from bot.tg.dc import Message, GetUpdatesResponse
from bot.models import TelegramUser
from goals.models.goal import Goal
from goals.models.goal_category import GoalCategory

# ----------------------------------------------------------------------------------------------------------------------
# Create logger instance
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)


# ----------------------------------------------------------------------------------------------------------------------
class BotMachine(object):
    """
    A finite state machine that represents the behavior of a Telegram bot

    Attributes:
        client: The Telegram client that the bot uses to communicate with users
        offset: The offset of the last update that the bot has processed
        update_count: The number of updates that have been processed
        bot: The 'Machine' instance that represents the bots state transitions
        controller: The controller of the bot with functional logic
        days: Delta for the due date of the goal
    """

    def __init__(self, client: TgClient):
        """
        Initialize the `BotMachine` instance

        Args:
            client: The Telegram client that the bot uses to communicate with users
        """
        self.client = client
        self.offset: int = 0
        self.update_count: int = 0
        self.bot = Machine(
            model=self,
            states=[
                "initialize",
                "verification",
                "main",
                "create_category",
                "create_goal",
            ],
            initial="main",
        )
        self.controller = Controller()
        self.days = 7

        # Add verification block transitions
        self.bot.add_transition(
            "go_to_verification",
            "initialize",
            "verification",
            after="verification_block",
        )
        # Add main block transitions
        self.bot.add_transition(
            "go_to_main", "verification", "main", after="main_block"
        )
        self.bot.add_transition(
            "go_to_initialize_from_main", "main", "initialize", after="initialize_block"
        )
        self.bot.add_transition(
            "go_to_verification_from_main",
            "main",
            "verification",
            after="verification_block",
        )
        # Add create category block transitions
        self.bot.add_transition(
            "go_to_create_category",
            "main",
            "create_category",
            after="create_category_block",
        )
        self.bot.add_transition(
            "go_to_initialize_from_create_category",
            "create_category",
            "initialize",
            after="initialize_block",
        )
        self.bot.add_transition(
            "go_to_main_from_create_category",
            "create_category",
            "main",
            after="main_block",
        )
        # Add create goal block transitions
        self.bot.add_transition(
            "go_to_create_goal",
            "create_category",
            "create_goal",
            after="create_goal_block",
        )
        self.bot.add_transition(
            "go_to_initialize_from_create_goal",
            "create_goal",
            "initialize",
            after="initialize_block",
        )
        self.bot.add_transition(
            "go_to_main_from_create_goal", "create_goal", "main", after="main_block"
        )
        # Add cancel transition
        self.bot.add_transition(
            "cancel", ["create_category", "create_goal"], "main", after="main_block"
        )

    # ----------------------------------------------------------------
    def initialize_block(self, message: Message) -> None:
        """
        Block with 'create a new user' logic

        Args:
            message: The message object containing user information

        Returns:
            None
        """
        logger.debug("== Initialize block ==")
        self.controller.create_telegram_user(self.client, message)
        self.go_to_verification()  # type: ignore

    # ----------------------------------------------------------------
    def verification_block(self) -> None:
        """
        Handles the verification process for users who are not yet verified

        Returns:
            None
        """
        logger.debug("== Verification block ==")
        while self.state == "verification":  # type: ignore
            update_order: GetUpdatesResponse = self.controller.update_order(
                self.client, self.offset
            )

            # Check result is not empty
            if update_order.result:
                for item in update_order.result:
                    self.offset = item.update_id + 1
                    message: Optional[Message] = item.message
                    user: Optional[TelegramUser] = self.controller.get_telegram_user(message.from_.id)  # type: ignore

                    # Check allowed command
                    if message.text == "/confirm":  # type: ignore
                        logger.debug("- Confirmed -")

                        if user.user:  # type: ignore
                            logger.debug("User found")
                            keyboard: list[list[str]] = [["/goals", "/create"]]
                            reply_markup: str = json.dumps({
                                "keyboard": keyboard,
                                "resize_keyboard": True,
                                "one_time_keyboard": False,
                            })
                            self.client.send_message(
                                chat_id=message.chat.id,  # type: ignore
                                text=f"Поздравляю, {message.from_.username}! "  # type: ignore
                                f"Вы подключили бота к приложению, "
                                f"теперь Вам доступны команды для получения или создания целей. \n"
                                f"Выберите одну из доступных команд:",
                                reply_markup=reply_markup,
                            )  # type: ignore
                            self.go_to_main()  # type: ignore

                        logger.debug("User not found, update code")
                        self.controller.update_verification_code(self.client, user)  # type: ignore

                    # Check not allowed commands
                    elif message.text in ("/start", "/cancel", "/goals", "/create"):  # type: ignore
                        logger.debug("- Command error -")
                        self.client.send_message(
                            chat_id=user.tg_chat_id,  # type: ignore
                            text=f"Вам недоступно выполнение команд",
                        )  # type: ignore

                    else:
                        logger.debug("- Unregistered command or text found -")
                        self.controller.update_verification_code(self.client, user)  # type: ignore

    # ----------------------------------------------------------------
    def main_block(self) -> None:
        """
        Main block with the chatbot logic

        Returns:
            None
        """
        logger.debug("== Main block ==")
        while self.state == "main":  # type: ignore
            update_order: GetUpdatesResponse = self.controller.update_order(
                self.client, self.offset
            )

            # Check result is not empty
            if update_order.result:
                for item in update_order.result:
                    self.offset = item.update_id + 1
                    message: Optional[Message] = item.message

                    if not message:
                        continue

                    user: Optional[TelegramUser] = self.controller.get_telegram_user(
                        message.from_.id
                    )
                    # Check user is not exist
                    if not user:
                        self.go_to_initialize_from_main(message)  # type: ignore

                    # Check user is not verified
                    if not user.user:  # type: ignore
                        self.go_to_verification_from_main()  # type: ignore

                    # Check allowed command
                    if item.message.text == "/goals":  # type: ignore
                        # Return a queryset of goals the user is a participant of
                        goals: QuerySet[Goal] = self.controller.get_goals(user)  # type: ignore

                        if not goals:
                            keyboard: list[list[str]] = [["/goals", "/create"]]
                            reply_markup: str = json.dumps({
                                "keyboard": keyboard,
                                "resize_keyboard": True,
                                "one_time_keyboard": False,
                            })

                            self.client.send_message(
                                chat_id=message.chat.id,
                                text=f"У Вас нет ни одной цели",
                                reply_markup=reply_markup,
                            )

                        for goal in goals:
                            self.client.send_message(
                                chat_id=message.chat.id,
                                text=f"Ваша цель: <a href='http://just-for.site/boards/{goal.category.board.id}"
                                f"/categories/{goal.category.id}/goals?goal={goal.id}'><b>{goal.title}</b></a> \n"
                                f"Категория: {goal.category} \n"
                                f"Доска: {goal.category.board} \n"
                                f"Подробности: {goal.description if goal.description != '' else 'Нет описания'}",
                                parse_mode="HTML",
                            )
                        logger.debug("- Get goals -")

                    # Check allowed command
                    elif item.message.text == "/create":  # type: ignore
                        categories: QuerySet[GoalCategory] = self.controller.get_categories(user)  # type: ignore
                        keyboard = [[category.title] for category in categories]
                        keyboard.append(["/cancel"])
                        reply_markup = json.dumps({
                            "keyboard": keyboard,
                            "resize_keyboard": True,
                            "one_time_keyboard": False,
                        })

                        self.client.send_message(
                            chat_id=message.chat.id,
                            text=f"Давайте создадим цель, вот список доступных категорий: ",
                            reply_markup=reply_markup,
                        )
                        self.go_to_create_category(message)  # type: ignore

                    else:
                        self.client.send_message(
                            chat_id=message.chat.id, text=f"Введена неверная команда"
                        )

    # ----------------------------------------------------------------
    def create_category_block(self, message: Message) -> None:
        """
        This block checks the name of the category entered by the user.
        If the category does not exist or the user does not have the necessary permissions
        to create a goal in that category, an error message will be sent.
        If the user cancels the category creation process by entering the '/cancel' command
        or if the client terminates the session, the block will return the user to the main block.

        Args:
            message: Message object that contains information about the message sent by the user

        Return:
            None
        """
        logger.debug("== Category block ==")
        last_message: Message = message
        while self.state == "create_category":  # type: ignore
            update_order: GetUpdatesResponse = self.controller.update_order(
                self.client, self.offset
            )

            # Check result is not empty
            if update_order.result:
                for item in update_order.result:
                    self.offset = item.update_id + 1
                    message = item.message  # type: ignore
                    user: Optional[TelegramUser] = self.controller.get_telegram_user(
                        message.from_.id
                    )

                    # Check user is not exist
                    if not user:
                        self.go_to_initialize_from_create_category(message)  # type: ignore

                    # Check allowed command
                    if message.text == "/cancel":
                        keyboard: list[list[str]] = [["/goals", "/create"]]
                        reply_markup: str = json.dumps({
                            "keyboard": keyboard,
                            "resize_keyboard": True,
                            "one_time_keyboard": False,
                        })

                        self.client.send_message(
                            chat_id=message.chat.id,
                            text=f"Создание цели отменено \n"
                            f"Выберите одну из доступных команд:",
                            reply_markup=reply_markup,
                        )
                        logger.debug("- Cancelled -")
                        self.cancel()  # type: ignore

                    category: Optional[GoalCategory] = self.controller.get_category(user, message)  # type: ignore

                    if category:
                        keyboard = [["/cancel"]]
                        reply_markup = json.dumps({
                            "keyboard": keyboard,
                            "resize_keyboard": True,
                            "one_time_keyboard": False,
                        })

                        self.client.send_message(
                            chat_id=message.chat.id,
                            text=f"Вы выбрали категорию <b>{category.title}</b>, теперь введите заголовок цели: ",
                            reply_markup=reply_markup,
                            parse_mode="HTML",
                        )
                        self.update_count = 0
                        self.go_to_create_goal(category, message)  # type: ignore

                    else:
                        self.client.send_message(
                            chat_id=message.chat.id,
                            text=f"Категории <b>{message.text}</b> не существует \n"
                            f"или у Вас нет прав для редактирования",
                            parse_mode="HTML",
                        )

            self.update_count += 1
            logger.debug(f"! Update cycles: {self.update_count} !")

            # Check update count for terminate session
            if self.update_count == 3:
                self.terminate_create_session(last_message)  # type: ignore

    # ----------------------------------------------------------------
    def create_goal_block(self, category, message) -> None:
        """
        This block wait the name of the goal entered by the user.
        If the user cancels the goal creation process by entering the '/cancel' command
        or if the client terminates the session, the block will return the user to the main block.

        Args:
            category: The category data for the goal creation process
            message: Message object that contains information about the message sent by the user

        Return:
            None
        """
        logger.debug("== Goal block ==")
        last_message: Message = message
        while self.state == "create_goal":  # type: ignore
            update_order: GetUpdatesResponse = self.controller.update_order(
                self.client, self.offset
            )

            # Check result is not empty
            if update_order.result:
                for item in update_order.result:
                    self.offset = item.update_id + 1
                    message = item.message
                    user: Optional[TelegramUser] = self.controller.get_telegram_user(
                        message.from_.id
                    )

                    # Check user is not exist
                    if not user:
                        self.go_to_initialize_from_create_goal(message)  # type: ignore

                    # Check allowed command
                    if message.text == "/cancel":
                        keyboard: list[list[str]] = [["/goals", "/create"]]
                        reply_markup: str = json.dumps({
                            "keyboard": keyboard,
                            "resize_keyboard": True,
                            "one_time_keyboard": False,
                        })

                        self.client.send_message(
                            chat_id=message.chat.id,
                            text=f"Создание цели отменено \n"
                            f"Выберите одну из доступных команд:",
                            reply_markup=reply_markup,
                        )
                        logger.debug("- Cancelled -")
                        self.cancel()  # type: ignore

                    # One week timedelta
                    # due_date: datetime = datetime.date.today() + datetime.timedelta(days=7)

                    goal: Goal = self.controller.create_goal(user, message, category, self.days)  # type: ignore

                    keyboard = [["/goals", "/create"]]
                    reply_markup = json.dumps({
                        "keyboard": keyboard,
                        "resize_keyboard": True,
                        "one_time_keyboard": False,
                    })

                    self.client.send_message(
                        chat_id=message.chat.id,
                        text=f"Ваша цель <a href='http://just-for.site/boards/{goal.category.board.id}"
                        f"/categories/{goal.category.id}/goals?goal={goal.id}'><b>{goal.title}</b></a> "
                        f"успешно создана! \n"
                        f"Вы можете посмотреть ее в приложении, перейдя по ссылке \n\n"
                        f"Выберите одну из доступных команд:",
                        reply_markup=reply_markup,
                        parse_mode="HTML",
                    )
                    logger.debug("- Goal created -")
                    self.go_to_main_from_create_goal()  # type: ignore

            self.update_count += 1
            logger.debug(f"! Update cycles: {self.update_count} !")

            # Check update count for terminate session
            if self.update_count == 3:
                self.terminate_create_session(last_message)  # type: ignore

    # ----------------------------------------------------------------
    def terminate_create_session(self, last_message: Message) -> None:
        """
        Terminate the current create session and return the user to the main block

        Args:
            last_message: Message object that contains information about the last message sent by the user

        Returns:
            None
        """
        keyboard: list[list[str]] = [["/goals", "/create"]]
        reply_markup: str = json.dumps(
            {"keyboard": keyboard, "resize_keyboard": True, "one_time_keyboard": False}
        )

        self.client.send_message(
            chat_id=last_message.chat.id,
            text=f"Сессия истекла \n" f"Выберите одну из доступных команд:",
            reply_markup=reply_markup,
        )
        logger.debug("- Session expired -")
        self.update_count = 0

        # Check current state
        if self.state == "create_goal":  # type: ignore
            self.go_to_main_from_create_goal()  # type: ignore
        self.go_to_main_from_create_category()  # type: ignore
