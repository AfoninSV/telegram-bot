from config_data.config import api_settings
import telebot
from telebot.storage import StateMemoryStorage

from utils.bot_commands import set_commands


storage = StateMemoryStorage()

# Initialisation bot app
bot = telebot.TeleBot(api_settings.tg_token.get_secret_value(),
                      state_storage=storage)
set_commands(bot)
