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

import json
import logging
import random
import argparse
from uuid import uuid4
from datetime import datetime, time

from telegram import (
    InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle,
    InputTextMessageContent, Update,
)
from telegram.constants import ParseMode
from telegram.ext import (
    Application, CommandHandler, ContextTypes, InlineQueryHandler,
    CallbackQueryHandler,
)

import constants
import secrets
from db_tools import ApprovalStates, DBTools
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
    notifying_time = time(hour=10),
    notifying_days = (0, 1, 2, 3, 4, 5, 6)

    def __init__(
        self, logging_level: int = logging.INFO, test_run: bool = False
    ):
        self.db_tools = DBTools(constants.DB_NAME)
        self.logging_level = logging_level
        self.test_run = test_run
        self.log_file = (
            f'logs/{self.__class__.__name__}.log'
            if not test_run
            else f'logs/{self.__class__.__name__}_dev.log'
        )
        setup_logger(
            self.__class__.__name__,
            log_file=self.log_file,
            level=logging_level
        )
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.debug(
            'Initialised %s', self.__class__.__name__
        )
        if self.test_run:
            self.logger.warning('It is a test run')

    # noinspection PyUnusedLocal
    async def start_command(
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
        self.logger.debug('Running /start command')
        text = 'commands: /help /about'
        if update.message.from_user.id == secrets.MAIN_ADMIN_TG_USER_ID:
            text += (
                '\nBecause you are an admin - you can use '
                '/notify_start, /notify_stop and /check_once commands 😉'
            )

        await update.message.reply_text(text)

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
        self.logger.debug('Running /help command')
        await update.message.reply_text(
            'There is only one person that can help you: '
            + '@' + secrets.MAIN_ADMIN_TG_USERNAME
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
        self.logger.debug('Running /about command')
        about_message = (
                'Check out source and suggest an issue: '
                + f'[GITHUB]({constants.GITHUB_URL})' + '\n'
                + 'Ask about this bot: '
                + '@' + secrets.MAIN_ADMIN_TG_USERNAME
        )
        await update.message.reply_text(
            about_message, parse_mode=ParseMode.MARKDOWN
        )

    # noinspection PyUnusedLocal
    async def suggest_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """
        This method handles the /suggest command. It logs the action,
        checks if the user exists in the database, if not it adds them.
        Then it saves the suggestion made by the user to the database.
        Finally, it sends a markdown styled reply text to the user.

        :param update: An object that encapsulates an incoming Update.
        :param context: Context registered for this update.
        :return: None
        """

        self.logger.debug(
            'Running /suggest command from user: %s with text: "%s"',
            update.message.from_user, update.message.text,
        )

        self.logger.debug(
            'Got suggestion from: %s', update.message.from_user
        )
        if not self.db_tools.user_exists(update.message.from_user.id):
            self.logger.debug(
                'New user, adding (%s)',
                update.message.from_user
            )
            self.db_tools.add_user(
                update.message.from_user.id, update.message.from_user.username
            )

        self.logger.debug('Saving prediction to database')
        if update.message.text == '/suggest':
            await update.message.reply_text(
                'Try to write something after "/suggest"', parse_mode=ParseMode.MARKDOWN
            )
        else:
            self.db_tools.add_prediction(
                update.message.text.removeprefix('/suggest '),
                update.message.from_user.id
            )

            await update.message.reply_text(
                'suggestion sent to approve', parse_mode=ParseMode.MARKDOWN
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

    # noinspection PyUnusedLocal
    async def notify_admin_unapproved_predictions(
        self,
        context: ContextTypes.DEFAULT_TYPE
    ):
        """
        Notify the admin if there are unapproved predictions
        in the DB with buttons to approve, reject or
        mark them as inappropriate.
        """

        self.logger.debug('Checking for unapproved prediction')

        unapproved_predictions = self.db_tools.get_unapproved_predictions()

        if unapproved_predictions:
            self.logger.debug('There are unapproved prediction')
            for prediction in unapproved_predictions:
                btn_approve = InlineKeyboardButton(
                    'Approve',
                    callback_data=(
                        json.dumps(
                            [{
                                'prediction_id': prediction[0],
                                'state': ApprovalStates.APPROVED.value
                            },
                            ]
                        ))
                )
                btn_reject = InlineKeyboardButton(
                    'Reject',
                    callback_data=(
                        json.dumps(
                            [{
                                'prediction_id': prediction[0],
                                'state': ApprovalStates.REJECTED.value
                            },
                            ]
                        ))
                )
                btn_inappropriate = InlineKeyboardButton(
                    'Mark as Inappropriate',
                    callback_data=(
                        json.dumps(
                            [{
                                'prediction_id': prediction[0],
                                'state': ApprovalStates.INAPPROPRIATE.value
                            },
                            ]
                        ))
                )

                reply_markup = InlineKeyboardMarkup(
                    [[btn_approve, btn_reject], [btn_inappropriate]]
                )

                self.logger.debug(
                    'Sending message with unapproved predictions'
                )

                await context.bot.send_message(
                    chat_id=secrets.MAIN_ADMIN_TG_USER_ID,
                    text=f"Prediction: {prediction[1]}",
                    reply_markup=reply_markup
                )
        elif self.test_run:
            self.logger.debug('There is no unapproved prediction')
            await context.bot.send_message(
                chat_id=secrets.MAIN_ADMIN_TG_USER_ID,
                text='You have no unapproved predictions',
            )

    def remove_job_if_exists(
        self, name: str, context: ContextTypes.DEFAULT_TYPE
    ) -> bool:
        """Remove job with given name. Returns whether job was removed."""
        current_jobs = context.job_queue.get_jobs_by_name(name)
        self.logger.debug(
            'Current jobs: %s', [job.name for job in context.job_queue.jobs()]
        )
        if not current_jobs:
            return False
        for job in current_jobs:
            job.schedule_removal()
        return True

    # noinspection PyUnusedLocal
    async def _start_unapproved_messages_notify_job(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE,
        run_once: bool = False
    ):
        """
        Starts the job of notifying about unapproved messages

        This method starts a job that periodically checks for unapproved
        messages and notifies the admin. It takes Update and
        Context objects as arguments and doesn't return anything.
        It also verifies if the user is an admin, if not,
        sends a message to the admin about the unauthorised attempt
        and notifies the user they are not authorised to do that.

        :param update: The incoming update object containing information
            about the incoming message.
        :type update: Update
        :param context: The context object for this update.
        :type context: ContextTypes.DEFAULT_TYPE
        :param run_once: If True, the job will run only once,
            otherwise it will run periodically.
        :type run_once: bool
        :return: None
        """
        # terminate if the user is not the admin
        if update.message.from_user.id != secrets.MAIN_ADMIN_TG_USER_ID:
            await context.bot.send_message(
                chat_id=secrets.MAIN_ADMIN_TG_USER_ID,
                text=(
                    'Someone tried to mess around: '
                    f'{update.message.from_user.username}'
                    f'({update.message.from_user.id})'
                )
            )
            await context.bot.send_message(
                chat_id=update.message.from_user.id,
                text='You can`t do that!'
            )
            return

        if run_once:
            context.job_queue.run_once(
                self.notify_admin_unapproved_predictions,
                when=datetime.now().minute + 1,
                name=str(secrets.MAIN_ADMIN_TG_USER_ID),
                user_id=secrets.MAIN_ADMIN_TG_USER_ID
            )
            await update.message.reply_text('Wait for it...')
        else:
            job_removed = self.remove_job_if_exists(
                str(secrets.MAIN_ADMIN_TG_USER_ID), context
            )
            text = "Starting job"
            if job_removed:
                text += ", old one was removed"
            self.logger.info(text)

            context.job_queue.run_daily(
                self.notify_admin_unapproved_predictions,
                time=self.notifying_time,
                days=self.notifying_days,
                name=str(secrets.MAIN_ADMIN_TG_USER_ID),
                user_id=secrets.MAIN_ADMIN_TG_USER_ID
            )

            await update.message.reply_text(text)

    # noinspection PyUnusedLocal
    async def stop_unapproved_messages_notify(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """
        Stops the job of notifying about unapproved messages if the user
        is an admin.

        This function first sends a message to the admin to notify about
        the stopping of the checks for unapproved predictions.
        Then it retrieves the job by its name from the queue and
        if it exists, schedules it for removal.

        If there was no job it sends a message to the admin stating
        that there were no jobs to stop.

        :param update: The incoming update object containing information
            about the incoming message.
        :type update: Update
        :param context: The context object providing additional
            information about the incoming message.
        :type context: ContextTypes.DEFAULT_TYPE
        """
        text = 'Stopping checking for unapproved predictions'
        await context.bot.send_message(
            chat_id=secrets.MAIN_ADMIN_TG_USER_ID,
            text=text
        )
        self.logger.debug(text)
        job = context.job_queue.get_jobs_by_name(str(secrets.MAIN_ADMIN_TG_USER_ID))
        if job:
            job[0].schedule_removal()
        else:
            await context.bot.send_message(
                chat_id=secrets.MAIN_ADMIN_TG_USER_ID,
                text='There were no jobs to stop'
            )

    async def start_unapproved_messages_notify(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """
        Starts the notifying job if the user is an admin.

        This function checks if the user is an admin and if true, calls
        the private function _start_unapproved_messages_notify_job to
        run the job.
        If the user is not an admin, this function does not do anything.

        :param update: The incoming update object containing information
            about the incoming message.
        :param context: The context object for this update.
        :type update: Update
        :type context: ContextTypes.DEFAULT_TYPE
        """
        await self._start_unapproved_messages_notify_job(
            update, context, run_once=False
        )

    async def check_unapproved_messages_once(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """
        Handles the inline query button action.

        This function gets the callback query, processes its data, and
        then executes corresponding actions.
        It first checks if the user, who pressed the button,
        is an admin or not. If not, it sends a warning message to
        the admin and the user and stops.

        Then, it updates the status of a prediction
        (specified in the callback query data) in the database.

        After processing the callback, it marks the query as answered
        and edits the original message sent with the buttons to display
        the result of the action.

        :param update: The incoming update object containing information
            about the incoming message.
        :param context: The context object for this update.
        :return: None
        """
        await self._start_unapproved_messages_notify_job(
            update, context, run_once=True
        )

    # noinspection PyUnusedLocal
    async def button_handler(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """
        Handles actions performed when a callback query button
        is clicked.

        This method validates that the button was clicked by
        the admin user.
        If a non-admin user attempts to click a button, a warning is
        logged and sent as a message to the admin.
        If the button clicker is verified to be the admin,
        the method proceeds to process the callback query,
        updating the status of the related  prediction in the database.

        After processing the callback, it answers the query to prevent
        possible client-side issues and modifies the original message
        to display the result of the action.

        :param update: The incoming update object containing information
            about the callback query.
        :type update: Update
        :param context: The context object providing additional
            information about callback query.
        :type context: ContextTypes.DEFAULT_TYPE
        :return: None
        """
        self.logger.debug('Processing callback query')

        query = update.callback_query
        # check that the button pusher is the admin
        if update.effective_user.id != secrets.MAIN_ADMIN_TG_USER_ID:
            self.logger.debug(
                'Someone tried to push button without permission: %s (%s)',
                update.effective_user.id, update.effective_user.name
            )
            await query.edit_message_text(text=f"Forbidden action")
            await query.answer()

        callback_data_dict = json.loads(query.data)[0]
        self.logger.debug(
            'Processing callback with: %s', callback_data_dict
        )

        # update a prediction with the data from callback
        self.db_tools.update_prediction_status(
            callback_data_dict['prediction_id'], callback_data_dict['state']
        )

        # CallbackQueries need to be answered, even if
        # no notification to the user is needed
        # Some clients may have trouble otherwise.
        # See https://core.telegram.org/bots/api#callbackquery
        await query.answer()

        await query.edit_message_text(
            text=(
                f'''Prediction "{query.message.text}" '''
                f'''(id:{callback_data_dict['prediction_id']}) '''
                f'''was marked as {callback_data_dict['state']}'''
            )
        )


def main() -> None:
    """Run the bot."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--test_run', help='If it is a test run',
        action='store_true'
    )
    args = parser.parse_args()

    is_test_run = args.test_run

    bot = KindPredictionsBot(
        logging_level=logging.DEBUG,
        test_run=True if is_test_run is True else False
    )
    try:
        # Create the Application and pass it your bot's token.
        application = Application.builder().token(
            secrets.API_TOKEN if not is_test_run else secrets.API_TOKEN_TEST
        ).build()

        # on different commands - answer in Telegram
        application.add_handler(
            CommandHandler(
                "start", bot.start_command
            )
        )
        application.add_handler(
            CommandHandler(
                "help", bot.help_command
            )
        )
        application.add_handler(
            CommandHandler(
                "about", bot.about_command
            )
        )
        application.add_handler(
            CommandHandler(
                "suggest", bot.suggest_command
            )
        )

        # Handler for callbacks from pressed buttons
        application.add_handler(CallbackQueryHandler(bot.button_handler))
        # on inline queries - show corresponding inline results
        application.add_handler(InlineQueryHandler(bot.inline_query))

        # start job for notifying about unapproved messages
        application.add_handler(
            CommandHandler(
                "notify_start", bot.start_unapproved_messages_notify
            )
        )
        application.add_handler(
            CommandHandler(
                "notify_stop", bot.stop_unapproved_messages_notify
            )
        )
        application.add_handler(
            CommandHandler(
                "check_once", bot.check_unapproved_messages_once
            )
        )

        # Run the bot until the user presses Ctrl-C
        application.run_polling(allowed_updates=Update.ALL_TYPES)

    except Exception as e:
        bot.logger.error(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
