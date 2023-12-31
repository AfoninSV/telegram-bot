from telebot.handler_backends import State, StatesGroup
from telebot.types import Message
from telebot import custom_filters

from loader import bot


bot.add_custom_filter(custom_filters.StateFilter(bot))


class ConversationStates(StatesGroup):
    cancel = State()  # cancel (waiting),
    wait_button = State()  # button_reply
    wait_range = State()  # custom command
    wait_random = State()  # wait for random
    wait_name = State()  # wait for meal name
    wait_ingredients = State()  # wait for ingredients
    list_reply = State()  # ask for list type


def get_user_state(message: Message):
    state = bot.get_state(message.from_user.id, chat_id=message.chat.id)
    return state


def set_user_state(message: Message, state: ConversationStates) -> None:
    bot.set_state(message.from_user.id, state, message.chat.id)
