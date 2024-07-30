# noinspection NonAsciiCharacters
"""
This Python script is a Telegram Bot that responds to a series of predefined commands.

The bot is capable of:
- Responding to the /start command informing the user about available commands.
- Responding to the /help command by forwarding the question to the main bot administrator.
- Responding to the /about command with the information about the bot
    including its source code link.
- Handling inline requests by returning a random percentage
    to fun question "Насколько ты булка?".
"""

import logging
from uuid import uuid4
import random

from telegram import (
    InlineQueryResultArticle, InputTextMessageContent, Update,
)
from telegram.constants import ParseMode
from telegram.ext import (
    Application, CommandHandler, ContextTypes, InlineQueryHandler,
)

import constants
import secrets
from db_tools import DBTools
from utils import setup_logger


class KindPredictionsBot:
    # noinspection NonAsciiCharacters
    """
        This class defines the KindPredictionsBot, an asynchronous
        Telegram Bot that responds to a series of predefined commands.
        The bot is capable of handling commands like /start, /help
        and /about as well as some inline queries.

        Attributes:
            db_tools (DBTools): Instance of the DBTools class that
                connects to and interacts with the bot's database.
            logging_level (int): Level of log detail. Uses the standard
                library logging levels.
            logger (logging.Logger): Logger instance used by the bot for
                debugging and error tracking.

        Methods:
            start(update: Update, context: ContextTypes.DEFAULT_TYPE):
                Handles the /start command informing the user
                    about available commands.
            help_command(
                    update: Update, context: ContextTypes.DEFAULT_TYPE):
                Handles the /help command by forwarding the question
                    to the main bot administrator.
            about_command(
                    update: Update, context: ContextTypes.DEFAULT_TYPE):
                Handles the /about command with the information about
                    the bot including its source code link.
            inline_query(
                    update: Update, context: ContextTypes.DEFAULT_TYPE):
                Handles inline requests by returning a random percentage
                    to fun question "Насколько ты булка?".
        """
    def __init__(self, logging_level: int = logging.INFO):
        self.db_tools = DBTools(constants.DB_NAME)
        self.logging_level = logging_level
        setup_logger(self.__class__.__name__, level=logging_level)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.debug('Initialised KindPredictionsBot')

    # noinspection PyUnusedLocal
    async def start(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """
        Handles the /start command informing the user about available
        commands.

        :param update: (Update) The incoming update object containing
            information about the incoming message.
        :param context: (ContextTypes.DEFAULT_TYPE) The context object
            for this update.
        :return: None
        """
        self.logger.debug('Running start command')
        await update.message.reply_text("commands: /help /about")

    # noinspection PyUnusedLocal
    async def help_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """
        This method handles the help command.
        It takes an Update object and a Context object as parameters
        and does not return anything. When invoked, it logs a
        debug message with the message "Running help command"
        and sends a text reply to the message with the username of
        the main admin.

        :param update: Update object that represents the incoming
            message or the edited message.
        :param context: Context object that provides information
            about the current state of the conversation.
        :return: None
        """
        self.logger.debug('Running help command')
        await update.message.reply_text(
            'There is only one person that can help you: '
            + '@' + constants.MAIN_ADMIN_TG_USERNAME
        )

    # noinspection PyUnusedLocal
    async def about_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """
        Handles the /about command with the information about the bot
        including its source code link.

        :param update: An object that represents the incoming message
            update.
        :type update: Update
        :param context: An object that provides additional context
            for the handler.
        :type context: ContextTypes.DEFAULT_TYPE
        :return: None
        """
        self.logger.debug('Running about command')
        about_message = (
                'Check out source and suggest an issue: '
                + f'[GITHUB]({constants.GITHUB_URL})' + '\n'
                + 'Ask about this bot: '
                + '@' + constants.MAIN_ADMIN_TG_USERNAME
        )
        await update.message.reply_text(
            about_message, parse_mode=ParseMode.MARKDOWN
        )

    # noinspection PyUnusedLocal
    async def inline_query(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """
        This method handles inline queries.
        It generates a list of InlineQueryResultArticle objects
        and answers the inline query.

        :param update: The update object containing information about
            the incoming update.
        :param context: The context object providing additional
            information and functionalities.
        :return: None
        """
        self.logger.debug('Running inline query')
        results = [
            InlineQueryResultArticle(
                id=str(uuid4()),
                title="Насколько ты булка?",
                input_message_content=InputTextMessageContent(
                    f"{str(random.randint(50, 100))}% булка!"
                ),
            ),
            InlineQueryResultArticle(
                id=str(uuid4()),
                title="Предсказание",
                input_message_content=InputTextMessageContent(
                    self.db_tools.get_random_approved_prediction()
                ),
            )
        ]
        await update.inline_query.answer(
            results,
            cache_time=constants.INLINE_QUERY_ANSWER_CACHE_TIMEOUT,
            is_personal=True
        )


def main() -> None:
    """Run the bot."""

    bot = KindPredictionsBot(logging_level=logging.DEBUG)

    # Create the Application and pass it your bot's token.
    application = Application.builder().token(secrets.API_TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", bot.start))
    application.add_handler(CommandHandler("help", bot.help_command))
    application.add_handler(CommandHandler(
        "about", bot.about_command
    ))

    # on inline queries - show corresponding inline results
    application.add_handler(InlineQueryHandler(bot.inline_query))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
