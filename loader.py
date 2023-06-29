from config_data.config import api_settings
from telegram_bot.commands import storage
import telebot

# Initialisation bot app
bot = telebot.TeleBot(api_settings.tg_token.get_secret_value(),
                      state_storage=storage)
