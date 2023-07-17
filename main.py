from config_data.config import api_settings
import telebot
from telebot.storage import StateMemoryStorage
from flask import Flask, request

import os

from telegram_bot import handlers
from utils.bot_commands import set_commands
from loader import bot


storage = StateMemoryStorage()
token = api_settings.tg_token.get_secret_value()

# Initialisations
server = Flask(__name__)


@server.route('/', methods=['POST'])
def getMessage():
    json_string = request.stream.read().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    print(bot.get_webhook_info())
    return f"{bot.get_webhook_info()}", 200


# @server.route("/")
# def webhook():
#     bot.remove_webhook()
#     bot.set_webhook(url='https://tg-tasty-bot-2f2c1b337730.herokuapp.com/' + token)
#     return "!", 200


set_commands(bot)
if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url='https://tg-tasty-bot-2f2c1b337730.herokuapp.com/' + token)
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
