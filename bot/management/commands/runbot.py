from django.core.management import BaseCommand

from diploma_project_pd12.settings import env

from bot.management.finite_state_machine import BotMachine
from bot.tg.client import TgClient


# ----------------------------------------------------------------------------------------------------------------------
# Create a new command
class Command(BaseCommand):
    help = "Run telegram echobot"

    def __init__(self, *args, **kwargs):
        self.client = TgClient(env("TG_TOKEN"))
        super().__init__(*args, **kwargs)

    def handle(self, *args, **kwargs) -> None:
        """
        The handle method is called when the command is executed.
        It calls the main_block method of the BotMachine instance to start the bot

        Return:
            None
        """
        bot = BotMachine(self.client)
        bot.main_block()
