from config_data.config import api_settings
import telebot
from telebot.storage import StateMemoryStorage

from utils.bot_commands import set_commands


storage = StateMemoryStorage()
token = api_settings.tg_token.get_secret_value()

# Initialisations
bot = telebot.TeleBot(token, state_storage=storage)

set_commands(bot)
