from config_data.config import api_settings
import telebot
from telebot.storage import StateMemoryStorage
from flask import Flask, request

import os

from utils.bot_commands import set_commands


storage = StateMemoryStorage()
token = api_settings.tg_token.get_secret_value()

# Initialisations
bot = telebot.TeleBot(token, state_storage=storage)
server = Flask(__name__)


@server.route('/' + token, methods=['POST'])
def get_message():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200


@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://www.heroku.com/pricing/estimates/10a196fdffb067183a041f4480e51e64d29c5e010cd192531b175d996886b46f' + token)
    return "!", 200


set_commands(bot)
