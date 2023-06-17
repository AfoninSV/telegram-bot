from config_data.config import api_settings
import telebot

# Initialisation bot app
bot = telebot.TeleBot(api_settings.tg_token.get_secret_value())
