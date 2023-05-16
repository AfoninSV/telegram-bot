from .commands import start
from telegram.ext import CommandHandler


start_handler = CommandHandler('start', start)
