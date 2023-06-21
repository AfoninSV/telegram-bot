from utils.helpers import start_message
from . import commands
from loader import bot
from telebot.types import Message


@bot.message_handler(commands=['start', 'help'])
def send_start(message: Message) -> None:
    """Sends message with commands and instructions"""
    bot.send_message(message.chat.id, start_message)


@bot.message_handler(commands=['low', 'high'])
def low_high_start(message: Message):
    next_step: int = commands.ask_category(message)
    commands.set_user_state(message, 2)


@bot.message_handler(func=lambda message: commands.get_user_state(message) == 2)
def low_command_reply(message: Message):
    commands.low_reply(message)


@bot.message_handler(func=lambda message: commands.get_user_state(message) == 3)
def high_command_reply(message: Message):
    commands.high_reply(message)
