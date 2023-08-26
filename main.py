from telebot.storage import StateMemoryStorage

from telegram_bot import handlers
from utils.bot_commands import set_commands
from loader import bot

storage = StateMemoryStorage()

set_commands(bot)

if __name__ == "__main__":
    bot.infinity_polling()
