from . import commands
from utils.helpers import start_message
from database.core import history_interface
from loader import bot
from telebot.types import Message


@bot.message_handler(commands=['cancel'])
def cancel(message: Message) -> None:
    history_interface.insert(user_id=message.from_user.id, message='/cancel')
    commands.set_user_state(message, 0)


@bot.message_handler(commands=['state'])
def cancel(message: Message) -> None:
    bot.send_message(message.chat.id, commands.get_user_state(message))


@bot.message_handler(commands=['start', 'help'])
def send_start(message: Message) -> None:
    """Sends message with commands and instructions"""

    if message.text == '/start':
        history_interface.insert(user_id=message.from_user.id, message='/start')
    elif message.text == '/help':
        history_interface.insert(user_id=message.from_user.id, message='/help')

    bot.send_message(message.chat.id, start_message)
    commands.set_user_state(message, 0)


@bot.message_handler(commands=['low', 'high'])
def low_high_start(message: Message) -> None:

    # write called command to db
    if message.text == '/low':
        history_interface.insert(user_id=message.from_user.id, message='/low')
    elif message.text == '/high':
        history_interface.insert(user_id=message.from_user.id, message='/high')

    commands.ask_category(message)


@bot.message_handler(func=lambda message: commands.get_user_state(message) == 2)
def low_command_reply(message: Message) -> None:
    commands.low_reply(message)


@bot.message_handler(func=lambda message: commands.get_user_state(message) == 3)
def high_command_reply(message: Message) -> None:
    commands.high_reply(message)


@bot.callback_query_handler(lambda call: True)
def button_for_recipe(call) -> None:
    """Handles the button callback query, retrieves the chosen recipe, and sends the recipe details"""
    commands.button(call)
