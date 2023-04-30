import datetime
import json
import secrets
from typing import Optional

from django.db.models import QuerySet
from transitions import Machine

from bot.tg.client import TgClient
from bot.tg.dc import Message, GetUpdatesResponse
from bot.models import TelegramUser
from goals.models.goal import Goal
from diploma_project_pd12.settings import RANDOM_STRING_CHARS
from goals.models.goal_category import GoalCategory


# ----------------------------------------------------------------------------------------------------------------------
class BotMachine(object):
    """
    A finite state machine that represents the behavior of a Telegram bot

    Attributes:
        client: The Telegram client that the bot uses to communicate with users
        offset: The offset of the last update that the bot has processed
        update_count: The number of updates that have been processed
        bot: The 'Machine' instance that represents the bot's state transitions
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
            states=['initialize', 'verification', 'main', 'create_category', 'create_goal'],
            initial='main'
        )

        # Add transitions for the states
        self.bot.add_transition('go_to_verification', 'initialize', 'verification',
                                after='verification_block')

        self.bot.add_transition('go_to_main', 'verification', 'main',
                                after='main_block')
        self.bot.add_transition('go_to_initialize_from_main', 'main', 'initialize',
                                after='initialize_block')
        self.bot.add_transition('go_to_verification_from_main', 'main', 'verification',
                                after='verification_block')

        self.bot.add_transition('go_to_create_category', 'main', 'create_category',
                                after='create_category_block')
        self.bot.add_transition('go_to_initialize_from_create_category', 'create_category', 'initialize',
                                after='initialize_block')
        self.bot.add_transition('go_to_main_from_create_category', 'create_category', 'main',
                                after='main_block')

        self.bot.add_transition('go_to_create_goal', 'create_category', 'create_goal',
                                after='create_goal_block')
        self.bot.add_transition('go_to_initialize_from_create_goal', 'create_goal', 'initialize',
                                after='initialize_block')
        self.bot.add_transition('go_to_main_from_create_goal', 'create_goal', 'main',
                                after='main_block')

        self.bot.add_transition('cancel', ['create_category', 'create_goal'], 'main',
                                after='main_block')

    # ----------------------------------------------------------------
    def initialize_block(self, message: Message) -> None:
        """
        Block with 'create a new user' logic

        Args:
            message: The message object containing user information

        Returns:
            None
        """
        print('== Блок инициализации ==')
        self.create_telegram_user(message)
        self.go_to_verification()

    # ----------------------------------------------------------------
    def verification_block(self) -> None:
        """
        Handles the verification process for users who are not yet verified

        Returns:
            None
        """
        print(f'== Блок верификации ==')
        while self.state == "verification":
            print(f'= Цикл блока верификации =')
            update_order: GetUpdatesResponse = self.update_order()

            # Check result is not empty
            if update_order.result:
                for item in update_order.result:
                    self.offset: int = item.update_id + 1
                    message: Optional[Message] = item.message
                    user: Optional[TelegramUser] = self.get_telegram_user(message.from_.id)

                    # Check if user is already verified
                    if user.user:
                        self.go_to_main()

                    # Check allowed command
                    if message.text == '/confirm':
                        print(f'Введено подтверждение')

                        if user.user:
                            print(f'Пользователь найден')
                            keyboard: list[list[str]] = [['/goals', '/create']]
                            reply_markup: str = json.dumps(
                                {'keyboard': keyboard,
                                 'resize_keyboard': True,
                                 'one_time_keyboard': False}
                            )
                            self.client.send_message(
                                chat_id=message.chat.id,
                                text=f"Поздравляю, {message.from_.username}! "
                                     f"Вы подключили бота к приложению, "
                                     f"теперь Вам доступны команды для получения или создания целей. \n"
                                     f"Выберите одну из доступных команд:",
                                reply_markup=reply_markup
                            )
                            self.go_to_main()

                        print(f'Пользователь не найден, код обновлен')
                        self.update_verification_code(user)

                    # Check not allowed commands
                    elif message.text in ('/start', '/cancel', '/goals', '/create'):
                        print(f'Введена неверная команда')
                        self.client.send_message(
                            chat_id=user.tg_chat_id,
                            text=f"Вам недоступно выполнение команд",
                        )

                    else:
                        print(f'Введен текст или команда')
                        self.update_verification_code(user)

    # ----------------------------------------------------------------
    def main_block(self) -> None:
        """
        Main block with the chatbot logic

        Returns:
            None
        """
        print(f'== Основной блок ==')
        while self.state == "main":
            print(f'= Цикл основного блока =')
            update_order: GetUpdatesResponse = self.update_order()

            # Check result is not empty
            if update_order.result:
                for item in update_order.result:
                    self.offset: int = item.update_id + 1
                    message: Optional[Message] = item.message

                    if not message:
                        continue

                    user: Optional[TelegramUser] = self.get_telegram_user(message.from_.id)
                    # Check user is not exist
                    if not user:
                        self.go_to_initialize_from_main(message)

                    # Check user is not verified
                    if not user.user:
                        self.go_to_verification_from_main()

                    # Check allowed command
                    if item.message.text == '/goals':
                        # Return a queryset of goals the user is a participant of
                        goals: QuerySet[Goal] = Goal.objects.select_related('category').filter(
                            category__board__participants__user=user.user,
                            category__board__is_deleted=False,
                            category__is_deleted=False
                        ).exclude(status=Goal.Status.archived)

                        if not goals:
                            keyboard: list[list[str]] = [['/goals', '/create']]
                            reply_markup: str = json.dumps(
                                {'keyboard': keyboard, 'resize_keyboard': True, 'one_time_keyboard': False})

                            self.client.send_message(
                                chat_id=message.chat.id,
                                text=f"У Вас нет ни одной цели",
                                reply_markup=reply_markup
                            )

                        for goal in goals:
                            self.client.send_message(
                                chat_id=message.chat.id,
                                text=f"Ваша цель: <a href='http://127.0.0.1/boards/{goal.category.board.id}"
                                     f"/categories/{goal.category.id}/goals?goal={goal.id}'><b>{goal.title}</b></a> \n"
                                     f"Категория: {goal.category} \n"
                                     f"Доска: {goal.category.board} \n"
                                     f"Подробности: {goal.description if goal.description != '' else 'Нет описания'}",
                                parse_mode='HTML'
                            )
                        print('Получены цели')

                    # Check allowed command
                    elif item.message.text == '/create':
                        categories: QuerySet[GoalCategory] = GoalCategory.objects.select_related('board').filter(
                            board__participants__role__in=[1, 2],
                            board__participants__user=user.user,
                            board__is_deleted=False,
                            is_deleted=False)
                        keyboard: list[list[str]] = [[category.title] for category in categories]
                        keyboard.append(['/cancel'])
                        reply_markup: str = json.dumps(
                            {'keyboard': keyboard, 'resize_keyboard': True, 'one_time_keyboard': False})

                        self.client.send_message(
                            chat_id=message.chat.id,
                            text=f"Давайте создадим цель, вот список доступных категорий: ",
                            reply_markup=reply_markup
                        )
                        self.go_to_create_category(message)

                    else:
                        self.client.send_message(
                            chat_id=message.chat.id,
                            text=f"Введена неверная команда"
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
        print(f'== Блок создания категории ==')
        last_message: Message = message
        while self.state == "create_category":
            update_order: GetUpdatesResponse = self.update_order()

            # Check result is not empty
            if update_order.result:
                for item in update_order.result:
                    self.offset: int = item.update_id + 1
                    message: Optional[Message] = item.message
                    user: Optional[TelegramUser] = self.get_telegram_user(message.from_.id)

                    # Check user is not exist
                    if not user:
                        self.go_to_initialize_from_create_category(message)

                    # Check allowed command
                    if message.text == '/cancel':
                        keyboard: list[list[str]] = [['/goals', '/create']]
                        reply_markup: str = json.dumps(
                            {'keyboard': keyboard, 'resize_keyboard': True, 'one_time_keyboard': False})

                        self.client.send_message(
                            chat_id=message.chat.id,
                            text=f"Создание цели отменено \n"
                                 f"Выберите одну из доступных команд:",
                            reply_markup=reply_markup
                        )
                        print(f'Отмена действия')
                        self.cancel()

                    category: [Optional[GoalCategory]] = GoalCategory.objects.select_related('board').filter(
                        board__participants__role__in=[1, 2],
                        title=message.text,
                        board__participants__user=user.user,
                        board__is_deleted=False,
                        is_deleted=False,
                    ).first()

                    if category:
                        self.client.send_message(
                            chat_id=message.chat.id,
                            text=f"Вы выбрали категорию <b>{category.title}</b>, теперь введите заголовок цели: ",
                            parse_mode='HTML'
                        )
                        self.update_count: int = 0
                        self.go_to_create_goal(category, message)

                    else:
                        self.client.send_message(
                            chat_id=message.chat.id,
                            text=f"Категории <b>{message.text}</b> не существует \n"
                                 f"или у Вас нет прав для редактирования",
                            parse_mode='HTML'
                        )

            self.update_count += 1
            print(f'Циклов ожидания прошло {self.update_count}')

            # Check update count for terminate session
            if self.update_count == 3:
                self.terminate_create_session(last_message)

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
        print(f'== Блок создания цели ==')
        last_message: Message = message
        while self.state == "create_goal":
            update_order: GetUpdatesResponse = self.update_order()

            # Check result is not empty
            if update_order.result:
                for item in update_order.result:
                    self.offset: int = item.update_id + 1
                    message: Optional[Message] = item.message
                    user: Optional[TelegramUser] = self.get_telegram_user(message.from_.id)

                    # Check user is not exist
                    if not user:
                        self.go_to_initialize_from_create_goal(message)

                    # Check allowed command
                    if message.text == '/cancel':
                        keyboard: list[list[str]] = [['/goals', '/create']]
                        reply_markup: str = json.dumps(
                            {'keyboard': keyboard, 'resize_keyboard': True, 'one_time_keyboard': False})

                        self.client.send_message(
                            chat_id=message.chat.id,
                            text=f"Создание цели отменено \n"
                                 f"Выберите одну из доступных команд:",
                            reply_markup=reply_markup
                        )
                        print(f'Отмена действия')
                        self.cancel()

                    # One week timedelta
                    due_date: datetime = datetime.date.today() + datetime.timedelta(days=7)

                    goal: Goal = Goal.objects.create(
                        user=user.user,
                        category=category,
                        title=message.text,
                        due_date=due_date.strftime('%Y-%m-%d')
                    )

                    keyboard: list[list[str]] = [['/goals', '/create']]
                    reply_markup: str = json.dumps(
                        {'keyboard': keyboard, 'resize_keyboard': True, 'one_time_keyboard': False})

                    self.client.send_message(
                        chat_id=message.chat.id,
                        text=f"Ваша цель <a href='http://http://just-for.site/boards/{goal.category.board.id}"
                             f"/categories/{goal.category.id}/goals?goal={goal.id}'><b>{goal.title}</b></a> "
                             f"успешно создана! \n"
                             f"Вы можете посмотреть ее в приложении, перейдя по ссылке",
                        reply_markup=reply_markup,
                        parse_mode='HTML'
                    )

                    self.go_to_main_from_create_goal()

            self.update_count += 1
            print(f'Циклов ожидания прошло {self.update_count}')

            # Check update count for terminate session
            if self.update_count == 3:
                self.terminate_create_session(last_message)

    # ----------------------------------------------------------------
    def create_telegram_user(self, message: Message) -> None:
        """
        Creates a new user and sends greeting message with verification code

        Args:
            message: The message object containing user information

        Return:
            None
        """
        verification_code: str = self.create_verification_code()

        TelegramUser.objects.create(
            tg_chat_id=message.chat.id,
            tg_username=message.from_.username,
            verification_code=verification_code
        )
        print("Пользователь создан")

        keyboard: list[list[str]] = [['/confirm']]
        reply_markup: str = json.dumps(
            {'keyboard': keyboard, 'resize_keyboard': True, 'one_time_keyboard': False, 'is_persistent': True})

        self.client.send_message(
            chat_id=message.chat.id,
            text=f"Добро пожаловать, {message.from_.username}!\n"
                 f"Ваш одноразовый код авторизации: {verification_code}\n"
                 f"После подтверждения кода в приложении вернитесь сюда и нажмите '/confirm' "
                 f"для завершения регистрации",
            reply_markup=reply_markup)
        print("Приветственное сообщение отправлено")

    # ----------------------------------------------------------------
    def get_telegram_user(self, chat_id: int) -> Optional[TelegramUser]:
        """
        Get TelegramUser object from database

        Args:
            chat_id: User chat id from Telegram

        Return:
            TelegramUser object if found otherwise None
        """
        try:
            user: TelegramUser = TelegramUser.objects.get(tg_chat_id=chat_id)
        except TelegramUser.DoesNotExist:
            return None

        return user

    # ----------------------------------------------------------------
    def create_verification_code(self, length=6, allowed_chars=RANDOM_STRING_CHARS) -> str:
        """
        Creates verification code

        Args:
            length: Code length
            allowed_chars: String with allowed chars

        Return:
            String with random generated verification code
        """
        return "".join(secrets.choice(allowed_chars) for _ in range(length))

    # ----------------------------------------------------------------
    def update_verification_code(self, user: TelegramUser) -> None:
        """
        Updates 'verification_code' field in user object and sends it to the chat

        Args:
            user: TelegramUser object

        Return:
            None
        """
        user.verification_code = self.create_verification_code()
        user.save(update_fields=('verification_code',))

        self.client.send_message(
            chat_id=user.tg_chat_id,
            text=f"Вы еще не подтвердили код в приложении \n"
                 f"Ваш новый одноразовый код авторизации: {user.verification_code} \n"
                 f"После подтверждения кода в приложении вернитесь сюда и нажмите '/confirm' "
                 f"для завершения регистрации",
        )

    # ----------------------------------------------------------------
    def update_order(self) -> GetUpdatesResponse:
        """
        Fetches updates from Telegram server

        Returns:
            GetUpdatesResponse: A response object that holds information about the updates returned by the API
        """
        return self.client.get_updates(offset=self.offset)

    # ----------------------------------------------------------------
    def terminate_create_session(self, last_message: Message) -> None:
        """
        Terminate the current create session and return the user to the main block

        Args:
            last_message: Message object that contains information about the last message sent by the user

        Returns:
            None
        """
        keyboard: list[list[str]] = [['/goals', '/create']]
        reply_markup: str = json.dumps(
            {'keyboard': keyboard, 'resize_keyboard': True, 'one_time_keyboard': False})

        self.client.send_message(
            chat_id=last_message.chat.id,
            text=f"Сессия истекла \n"
                 f"Выберите одну из доступных команд:",
            reply_markup=reply_markup
        )
        print(f'Сессия истекла')
        self.update_count: int = 0

        # Check current state
        if self.state == 'create_goal':
            self.go_to_main_from_create_goal()
        self.go_to_main_from_create_category()
