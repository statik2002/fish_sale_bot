import argparse
import logging
import os
from pprint import pprint
from textwrap import dedent

import redis
import telegram
from functools import partial
from dotenv import load_dotenv
from environs import Env
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (Updater, CommandHandler,
                          MessageHandler, Filters,
                          CallbackContext, ConversationHandler, CallbackQueryHandler)

from auth import get_all_products, get_access_token, get_product, get_inventory, get_product_image_url, \
    get_product_unit, get_product_price
from error_processing import TelegramLogsHandler

logger = logging.getLogger(__file__)

START, BUTTONS_HANDLER, HANDLE_MENU, HANDLE_DESCRIPTION = range(4)


def start(update: Update, context: CallbackContext, token, redis_client) -> None:

    products = get_all_products(token)['data']
    #print(products)
    keyboard = []
    for product in products:
        keyboard.append([InlineKeyboardButton(product['attributes']['name'], callback_data=product['id'])])

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(
        'Выберете рыбов!',
        reply_markup=reply_markup,
    )

    return BUTTONS_HANDLER


def buttons_handler(
        update: Update,
        context: CallbackContext,
        token,
        redis_client) -> None:

    query = update.callback_query
    product = get_product(token, query.data)

    inventory = get_inventory(token, query.data)['data']

    image_url = get_product_image_url(token, product)
    unit = get_product_unit(product)
    price = get_product_price(product)

    message = dedent(f'''\
            {product.get('data').get('attributes').get('name')}
            
            {price} per {unit}
            
            {inventory['available']} {unit} on stock
            
            {product['data']["attributes"]["description"]}'''
    )

    keyboard = []
    keyboard.append([InlineKeyboardButton('Взад', callback_data=token)])
    reply_markup = InlineKeyboardMarkup(keyboard)

    context.bot.sendPhoto(chat_id=update.callback_query.message.chat.id, photo=image_url, caption=message, reply_markup=reply_markup)
    context.bot.delete_message(chat_id=update.callback_query.message.chat.id, message_id=update.callback_query.message.message_id)


    #context.bot.sendMessage(chat_id=update.callback_query.message.chat.id, text=message)
    #update.message.reply_text(message)

    #print(query)
    return HANDLE_MENU


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
        token=elastic_path_token,
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
            HANDLE_MENU: [
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
