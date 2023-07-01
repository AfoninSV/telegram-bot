from telebot.types import Message

from . import commands
from .states import ConversationStates, get_user_state
from utils.helpers import start_message, get_last_n_from_history
from database.core import history_interface
from loader import bot


@bot.message_handler(commands=['cancel'])
def cancel(message: Message) -> None:
    history_interface.insert(user_id=message.from_user.id, message='/cancel')
    commands.set_user_state(message, ConversationStates.cancel)


@bot.message_handler(commands=['state'])
def cancel(message: Message) -> None:
    # Used for debug
    state = get_user_state(message)
    if state:
        bot.send_message(message.chat.id, state)


@bot.message_handler(commands=['id'])
def cancel(message: Message) -> None:
    # Used for debug
    bot.send_message(message.chat.id, f'User: {message.from_user.id}\nChat: {message.chat.id}')


@bot.message_handler(commands=['start', 'help'])
def send_start(message: Message) -> None:
    """Sends message with commands and instructions"""

    if message.text == '/start':
        history_interface.insert(user_id=message.from_user.id, message='/start')
    elif message.text == '/help':
        history_interface.insert(user_id=message.from_user.id, message='/help')

    bot.send_message(message.chat.id, start_message)
    commands.set_user_state(message, ConversationStates.cancel)


@bot.message_handler(commands=['low', 'high'])
def low_high_start(message: Message) -> None:

    # write called command to db
    if message.text == '/low':
        history_interface.insert(user_id=message.from_user.id, message='/low')
    elif message.text == '/high':
        history_interface.insert(user_id=message.from_user.id, message='/high')

    commands.ask_category(message)


@bot.message_handler(commands=['random'])
def random(message: Message) -> None:
    commands.set_user_state(message, ConversationStates.wait_random)
    commands.random_recipe(message)


@bot.message_handler(commands=['list'])
def list_start(message: Message) -> None:
    commands.set_user_state(message, ConversationStates.list_reply)
    commands.ask_for_list(message)


@bot.message_handler(commands=['history'])
def history(message: Message) -> None:
    history_reply = get_last_n_from_history(10, str(message.from_user.id))
    reply_str = '\n'.join(history_reply)
    bot.send_message(message.chat.id, reply_str)


# state handlers

@bot.message_handler(state=ConversationStates.low_reply)
def low_command_reply(message: Message) -> None:
    commands.low_reply(message)


@bot.message_handler(state=ConversationStates.high_reply)
def high_command_reply(message: Message) -> None:
    commands.high_reply(message)


@bot.callback_query_handler(lambda call: True)
def button(call) -> None:
    """Handles the button callback query, retrieves the chosen recipe, and sends the recipe details"""

    if call.data.isdigit():
        commands.lh_button_get(call)
    elif call.data in {'areas', 'categories', 'ingredients'}:
        commands.set_user_state(call.message, ConversationStates.list_reply)
        commands.list_reply(call.message, commands.ListFactors.__dict__.get(call.data))
