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
# from db_tools import DBTools

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.DEBUG
)
# set higher logging level for httpx to avoid all GET and POST requests
# being logged
logging.getLogger(__name__).setLevel(logging.DEBUG)
logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update
# and context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    This method is used to handle the start command.

    :param update: An instance of the Update class representing the incoming update.
    :param context: An instance of the ContextTypes.DEFAULT_TYPE class
        representing the bot's context.
    :return: None
    """
    await update.message.reply_text("commands: //help //about")


async def help_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text(
        'There is only one person that can help you: '
        + '@' + constants.MAIN_ADMIN_TG_USERNAME
    )


async def about_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Send a message when the command /about is issued."""
    about_message = (
        'Check out source and suggest an issue: '
        + f'[GITHUB]({constants.GITHUB_URL})' + '\n'
        + 'Ask about this bot: '
        + '@' + constants.MAIN_ADMIN_TG_USERNAME
    )
    await update.message.reply_text(
        about_message, parse_mode=ParseMode.MARKDOWN
    )


async def inline_query(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Handle the inline query. This is run when you type: @botusername <query>
    """
    # query = update.inline_query.query

    # we don`t care about the context
    results = [
        InlineQueryResultArticle(
            id=str(uuid4()),
            title="Насколько ты булка?",
            input_message_content=InputTextMessageContent(
                f"{str(random.randint(50, 100))}% булка!"
            ),
        )
    ]

    await update.inline_query.answer(results, cache_time=0, is_personal=True)


def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(constants.API_TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("about", about_command))

    # on inline queries - show corresponding inline results
    application.add_handler(InlineQueryHandler(inline_query))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
