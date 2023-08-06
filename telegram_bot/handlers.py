from telebot.types import Message

import json

from . import commands
from .states import ConversationStates, get_user_state, set_user_state
from utils.helpers import start_message, help_message, get_last_n_from_history
from database.core import history_interface, favorites_interface
from loader import bot


@bot.message_handler(func=lambda message: "hello" in message.text.lower())
def cancel(message: Message) -> None:
    bot.send_message(message.chat.id, "Hello, dear friend! It's nice to see you.")


@bot.message_handler(commands=["cancel"])
def cancel(message: Message) -> None:
    commands.set_user_state(message, ConversationStates.cancel)


@bot.message_handler(commands=["state"])
def cancel(message: Message) -> None:
    # Used for debug
    state = get_user_state(message)
    if state:
        bot.send_message(message.chat.id, state)


@bot.message_handler(commands=["id"])
def cancel(message: Message) -> None:
    # Used for debug
    bot.send_message(
        message.chat.id, f"User: {message.from_user.id}\nChat: {message.chat.id}"
    )


# standard user commands


@bot.message_handler(commands=["start"])
def send_start(message: Message) -> None:
    """Sends welcoming message"""

    history_interface.insert(user_id=message.from_user.id, message="/start")
    bot.send_message(message.chat.id, start_message)
    commands.set_user_state(message, ConversationStates.cancel)


@bot.message_handler(commands=["help"])
def send_start(message: Message) -> None:
    """Send message with commands and instructions"""
    history_interface.insert(user_id=message.from_user.id, message="/help")
    bot.send_message(message.chat.id, help_message)
    commands.set_user_state(message, ConversationStates.cancel)


@bot.message_handler(commands=["low", "high"])
def low_high_start(message: Message) -> None:
    # write called command to db
    if message.text == "/low":
        history_interface.insert(user_id=message.from_user.id, message="/low")
    elif message.text == "/high":
        history_interface.insert(user_id=message.from_user.id, message="/high")

    commands.ask_category(message)


@bot.message_handler(commands=["custom"])
def custom(message: Message):
    history_interface.insert(user_id=message.from_user.id, message="/custom")
    ask_string = "Please write the range of ingredient quantities:\n\nFormat: 'number, number' or 'single number'"
    commands.ask_for(message, ask_string, state=ConversationStates.wait_range)


@bot.message_handler(commands=["random"])
def random(message: Message) -> None:
    history_interface.insert(user_id=message.from_user.id, message="/random")
    commands.set_user_state(message, ConversationStates.wait_random)
    commands.random_recipe(message)


@bot.message_handler(commands=["list"])
def list_start(message: Message) -> None:
    history_interface.insert(user_id=message.from_user.id, message="/list")
    commands.set_user_state(message, ConversationStates.list_reply)
    commands.ask_for_list(message)


@bot.message_handler(commands=["search"])
def search_start(message: Message) -> None:
    history_interface.insert(user_id=message.from_user.id, message="/search")
    commands.set_user_state(message, ConversationStates.wait_button)
    reply_data = ["by name", "by ingredients"]
    commands.reply_markup(
        message,
        "Select which search would you like to perform:",
        button_text=reply_data,
        callback_data=reply_data,
    )


@bot.message_handler(commands=["favorites"])
def list_start(message: Message) -> None:
    history_interface.insert(user_id=message.from_user.id, message="/favorites")
    commands.show_favorites(message)


@bot.message_handler(commands=["history"])
def history(message: Message) -> None:
    history_reply = get_last_n_from_history(10, int(message.from_user.id))
    if history_reply:
        reply_str = map(lambda tpl: f"{tpl[0]}: {tpl[1]}", history_reply)
        reply_str = "\n".join(list(reply_str))
        bot.send_message(message.chat.id, reply_str)
    else:
        bot.send_message(message.chat.id, "History is empty, welcome on board!")
    history_interface.insert(user_id=message.from_user.id, message="/history")


# state handlers


@bot.message_handler(state=ConversationStates.wait_range)
def find_meals_range(message: Message):
    given_range = message.text
    if range_list := commands.check_range(given_range):
        bot.send_message(message.chat.id, "Searching...")
        meals_found = commands.check_all_for_qty(range_list)

        if not meals_found:
            bot.send_message(message.chat.id, "Sorry, nothing found.")
            return

        commands.reply_markup(
            message, "Chose meal to see recipe:", meals_list=meals_found
        )
    else:
        bot.send_message(message.chat.id, "Wrong range, please check your numbers.")


@bot.message_handler(state=ConversationStates.wait_name)
def respond_for_name(message: Message):
    commands.find_by_name(message, message.text)


@bot.message_handler(state=ConversationStates.wait_ingredients)
def respond_for_ingredients(message: Message):
    if ingredients_list := commands.check_ingredients_list(message):
        commands.reply_search_by_ingredients(message, ingredients_list)
    else:
        bot.send_message(
            message.chat.id,
            "Sorry, nothing found. Please, check your ingredients list.",
        )


@bot.callback_query_handler(lambda call: True)
def button(call) -> None:
    """Handles the button callback query, retrieves the chosen recipe, and sends the recipe details"""

    msg = call.message
    if msg.from_user.is_bot:
        msg.from_user.id = msg.chat.id
    uid = msg.from_user.id
    cid = call.message.chat.id

    if call.data.isdigit():
        commands.meal_id_button_get(call)

    elif call.data in {"areas", "categories", "ingredients"}:
        commands.set_user_state(msg, ConversationStates.list_reply)
        commands.list_reply(msg, commands.Factors.__dict__.get(call.data))

    elif "filter" in call.data:
        call.data = call.data.split()[1]
        if call.data in commands.AREAS:
            commands.reply_areas(msg, call.data)

        elif call.data in commands.CATEGORIES:
            commands.reply_categories(msg, call.data)

    elif "add" in call.data:
        data: str = call.data.split("|")[1]
        commands.add_favorites(msg, data)

    elif "delete" in call.data:
        meal_id: str = call.data.split("|")[1]
        commands.delete_favorite(msg, meal_id)

    elif call.data in commands.CATEGORIES:
        last_command = get_last_n_from_history(1, msg.from_user.id)[0][1]

        if last_command == "/low":
            commands.low_reply(call)
        elif last_command == "/high":
            commands.high_reply(call)

    elif call.data == "by name":
        commands.ask_for(
            msg,
            "Please, write meal name to search:",
            state=ConversationStates.wait_name,
        )

    elif call.data == "by ingredients":
        commands.ask_for(
            msg,
            "Please, write ingredients separated by comma",
            state=ConversationStates.wait_ingredients,
        )

    elif call.data == "cancel":
        set_user_state(msg, ConversationStates.cancel)
        bot.send_message(msg.chat.id, "Enjoy!.")
