from config_data.config import api_settings
import telebot
from telebot.storage import StateMemoryStorage
from flask import Flask, request

import os

from telegram_bot import handlers
from utils.bot_commands import set_commands


storage = StateMemoryStorage()
token = api_settings.tg_token.get_secret_value()

# Initialisations
bot = telebot.TeleBot(token, state_storage=storage)
server = Flask(__name__)


@server.route('/' + token, methods=['POST'])
def get_message():
    json_string = request.stream.read().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200


@server.route("/", methods=['POST'])
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://tg-tasty-bot-2f2c1b337730.herokuapp.com/' + token)
    return "!", 200


set_commands(bot)
if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
