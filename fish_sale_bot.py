import argparse
import logging
import os
import redis
import telegram
from functools import partial
from dotenv import load_dotenv
from environs import Env
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (Updater, CommandHandler,
                          MessageHandler, Filters,
                          CallbackContext, ConversationHandler, CallbackQueryHandler)

from auth import get_all_products, get_access_token
from error_processing import TelegramLogsHandler

logger = logging.getLogger(__file__)

START, BUTTONS_HANDLER, ATTEMPT = range(3)


def start(update: Update, context: CallbackContext, token) -> None:

    products = get_all_products(token)
    print(products)

    keyboard = [[InlineKeyboardButton("Option 1", callback_data='1'),
                 InlineKeyboardButton("Option 2", callback_data='2')],

                [InlineKeyboardButton("Option 3", callback_data='3')]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(
        'Выберете рыбов!',
        reply_markup=reply_markup,
    )

    return BUTTONS_HANDLER


def buttons_handler(
        update: Update,
        context: CallbackContext,
        redis_client) -> None:

    query = update.callback_query

    message = "Selected option: {}".format(query.data)

    #print(query)


def cancel(bot, update):
    user = update.message.from_user
    logger.info("Пользователь %s завершил покупку.", user.first_name)
    update.message.reply_text('Пока пока!',
                              reply_markup=telegram.ReplyKeyboardRemove())

    return ConversationHandler.END


def error_handler(update, context):
    logger.error(msg='Ошибка при работе скрипта: ', exc_info=context.error)


def main() -> None:
    env = Env()
    env.read_env()
    telegram_token = env('TELEGRAM_TOKEN')
    chat_id = env('CHAT_ID')
    elastic_path_client_id = env('ELASTIC_PATH_CLIENT_ID')

    redis_client = redis.StrictRedis(
        host=env('REDIS_HOST'),
        port=env('REDIS_PORT'),
        password=env('REDIS_PASSWORD'),
        charset="utf-8",
        decode_responses=True
    )

    service_bot = telegram.Bot(token=telegram_token)
    logging.basicConfig(level=logging.ERROR)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(TelegramLogsHandler(service_bot, chat_id))

    updater = Updater(telegram_token)
    dispatcher = updater.dispatcher

    elastic_path_token = get_access_token(elastic_path_client_id)
    partial_start_handler = partial(
        start,
        redis_client=redis_client,
        token=elastic_path_token
    )
    partial_buttons_handler = partial(
        buttons_handler,
        redis_client=redis_client
    )

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', partial_start_handler)],
        states={
            BUTTONS_HANDLER: [
                CallbackQueryHandler(
                    partial_buttons_handler,
                )
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dispatcher.add_handler(conv_handler)
    dispatcher.add_error_handler(error_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
