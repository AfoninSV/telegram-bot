from typing import Optional
from string import ascii_lowercase
import re
import json

from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from api_mealdb import api
from loader import bot, storage
from utils.helpers import Factors, get_last_n_from_history
from .states import ConversationStates, set_user_state
from database.core import history_interface

"""
states:
    0: cancel (waiting),
    1: ask_category,
    2: low_reply,
    3: high_reply,
    4: button_reply
    5: wait for random
    6: ask for list type
    7: wait for range
"""


def ask_category(message) -> None:    #TODO change string to markup
    """Send message asking to input desired category"""

    last_command = get_last_n_from_history(1, message.from_user.id)[0][1]
    categories_str = ", ".join(api.get_list_by_key(Factors.categories))
    bot.send_message(message.chat.id, f'Available categories:\n{categories_str}')
    bot.send_message(message.chat.id, 'Please enter the category name:')


    if last_command == '/low':
        set_user_state(message, ConversationStates.low_reply)
    elif last_command == '/high':
        set_user_state(message, ConversationStates.high_reply)


def category_not_found(message: Message) -> None:
    """Sends message informing that looked database wasn't found and
    sends existed fields"""

    categories_str = ", ".join(api.get_list_by_key(Factors.categories))
    bot.send_message(message.chat.id, f'Category not found, please see categories below: '
                                      f'\n\n{categories_str}')
    bot.send_message(message.chat.id, "Try again: ")


def category_meals_found(message: Message, result: list) -> int:
    """Sends a list of meals within provided list and asks the user to choose a meal"""

    keyboard = InlineKeyboardMarkup()
    for i_meal, meal in enumerate(result, start=1):
        bot.send_photo(message.chat.id,
                       f"{meal.get('strMealThumb')}\n",
                       caption=f"{i_meal}: {meal['strMeal']}" \
                               f"\n    {meal['ingredients_qty']} ingredients\n")
        button = InlineKeyboardButton(text=i_meal,
                                      callback_data=meal.get('idMeal'))
        keyboard.add(button)

    bot.send_message(message.chat.id, "Please choose meal to get recipe:", reply_markup=keyboard)
    set_user_state(message, ConversationStates.cancel)


def low_high_reply(message: Message,
                   func=api.low) -> None:
    """Base function for low_reply, high_reply.
    Processes the user input for a category and searches based on the category name.
    Used for /low and /high commands."""

    bot.send_message(message.chat.id, 'Searching...')
    category_name = message.text
    result = func(category_name)

    if result is None:
        category_not_found(message)
    else:
        category_meals_found(message, result)
        set_user_state(message, ConversationStates.wait_button)

def low_reply(message: Message):
    low_high_reply(message)

def high_reply(message: Message):
    low_high_reply(message, func=api.high)


def cancel(message: Message) -> None:
    """Send notification that operation was canceled"""
    bot.send_message(message.chat.id, 'Operation cancelled.')


def get_recipe_str(meal_id: Optional[str]=None, meal:Optional[dict]=None) -> tuple[str]:
    """Retrieves the recipe for a given meal ID and returns the recipe picture and text"""

    if meal_id:
        meal = api.get_meal_by_id(meal_id)

        ingredients_str = api.get_meal_ingredients(meal_id).strip()
        link = meal.get('strYoutube')
    else:
        ingredients_str = api.get_meal_ingredients(meal.get('idMeal')).strip()
        link = meal.get('strYoutube')

    reply_str = str()
    reply_str += f"Name: {meal.get('strMeal')}\n" \
                 f"Category: {meal.get('strCategory')}\n" \
                 f"Area: {meal.get('strArea')}\n" \
                 f"Ingredients: {ingredients_str}" \
                 f"\n\nInstruction:\n {meal.get('strInstructions')}\n" \
                 f"{link}"
    return meal.get("strMealThumb"), reply_str


def send_recipe_str(recipe_picture: str, recipe_str: str, message: Message) -> None:
    bot.send_photo(message.chat.id, recipe_picture)
    if len(recipe_str) > 4096:
        recipe_str_1 = recipe_str[:recipe_str // 2]
        recipe_str_2 = recipe_str_1[recipe_str // 2 + 1:]
        bot.send_message(message.chat.id, recipe_str_1)
        bot.send_message(message.chat.id, recipe_str_2)
    else:
        bot.send_message(message.chat.id, recipe_str)


def send_multiple_recipes(message: Message, meals_list: list) -> None:
    for i_meal, meal in enumerate(meals_list):
        if i_meal >= 2:
            set_user_state(message, ConversationStates.wait_button)
            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['meals_list'] = meals_list

            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton(text='Yes', callback_data='meals_list'))
            keyboard.add(InlineKeyboardButton(text='Cancel', callback_data='cancel'))
            bot.send_message(message.chat.id, 'Show more?', reply_markup=keyboard)


            break
        send_recipe_str(*get_recipe_str(meal=meal), message)
        meals_list.pop(i_meal)
    else:
        set_user_state(message, ConversationStates.cancel)


def meal_id_button_get(call) -> None:
    """Handles the button callback query, retrieves the chosen recipe, and sends the recipe details"""

    chosen_id = call.data
    send_recipe_str(*get_recipe_str(meal_id=chosen_id), call.message)
    set_user_state(call.message, ConversationStates.cancel)


def ask_for(message: Message, ask_text: str,
            state: Optional[ConversationStates]=None) -> None:
    bot.send_message(message.chat.id, ask_text)

    if state:
        set_user_state(message, state)


def check_range(range_str: str) -> bool | list:
    if match := re.match(r'\d+,\s*\d+', range_str):
        start, end = re.split(r',\s*', match.group(0))
        start = int(start)
        end = int(end)
        if end < start:
            return False
        if match.group(0) != range_str:
            return False
        return list(range(start, end + 1))

    if match := re.match(r'\d+', range_str):
        if match.group(0) != range_str:
            return False
        return [int(match.group(0))]


def check_all_for_qty(qty_range: list) -> list[dict]:
    fit = list()
    for letter in ascii_lowercase:
        meals: list = api.meals_by_first_letter(letter)
        if meals:
            for meal in meals:
                if (qty := api.get_ingredients_qty(meal.get('idMeal'))) in qty_range:
                    fit.append(meal)
    return fit



def random_recipe(message: Message) -> None:
    random_recipe: dict = api.get_random_meal()
    send_recipe_str(*get_recipe_str(meal=random_recipe), message)
    set_user_state(message, ConversationStates.cancel)


def ask_for_list(message: Message) -> None:
    """Sends message asking for type of list and make buttons for reply"""

    keyboard = InlineKeyboardMarkup()
    for type in {'areas', 'categories', 'ingredients'}:
        button = InlineKeyboardButton(text=type,
                                      callback_data=type)
        keyboard.add(button)

    bot.send_message(message.chat.id, 'Please choose the type of desired list:', reply_markup=keyboard)
    set_user_state(message, ConversationStates.cancel)


def list_reply(message: Message, factor: str) -> None:
    names_list = api.get_list_by_key(factor)
    names_str = ", ".join(names_list)
    if len(names_str) > 4096:
        list_len = len(names_list)
        names_str_1 = ", ".join(names_list[:list_len // 2])
        names_str_2 = ", ".join(names_list[list_len // 2 + 1 :])

        bot.send_message(message.chat.id, names_str_1)
        bot.send_message(message.chat.id, names_str_2)
    else:
        bot.send_message(message.chat.id, names_str)
    set_user_state(message, ConversationStates.cancel)


def find_by_name(message: Message, name: str) -> None:
    if meals := api.get_meal_by_name(name):
        if len(meals) == 1:
            send_recipe_str(*get_recipe_str(meal=meals[0]), message)
            set_user_state(message, ConversationStates.cancel)
        else:
            keyboard = InlineKeyboardMarkup()
            for meal in meals:
                meal_name = meal.get('strMeal')
                meal_id = meal.get('idMeal')
                keyboard.add(InlineKeyboardButton(meal_name, callback_data=meal_id))
            bot.send_message(message.chat.id, 'Chose meal you want to see:', reply_markup=keyboard)

    else:
        bot.send_message(message.chat.id, 'Nothing found, try again:')


def check_ingredinets_list(message: Message) -> list:
    """Turns string list divided by commas with list of words,
    whitespaces are changed with _ """

    ingredients_string = message.text.strip()
    ingredients_list = re.split(r',\s*', ingredients_string.lower())
    ingredients_list = [re.sub(r'\s+', '_', name) if re.search(r'\s+', name) else name
                        for name in ingredients_list]
    return ingredients_list


def reply_search_by_ingredients(message: Message, ingredients_list: list):
    ingredients = ','.join(ingredients_list)
    meals: list = api.search_by_ingredients(ingredients)
    if meals:
        keyboard = InlineKeyboardMarkup()
        for name, id in [(meal.get('strMeal'), meal.get('idMeal')) for meal in meals]:
            keyboard.add(InlineKeyboardButton(name, callback_data=id))
        bot.send_message(message.chat.id, 'Select which meal would you like to see:',
                         reply_markup=keyboard)
        set_user_state(message, ConversationStates.cancel)
    else:
        bot.send_message(message.chat.id, 'Nothing found, try again:')

def reply_markup(message, msg_to_ask: str,
                 button_text: list=None,
                 callback_data: list=None,
                 meals_list=None) -> None:
    """Sends message with keyboard markup with given data"""

    keyboard = InlineKeyboardMarkup()
    if meals_list:
        button_text = list()
        callback_data = list()
        for meal in meals_list:
            button_text.append(meal.get('strMeal'))
            callback_data.append(meal.get('idMeal'))

    for txt, id in zip(button_text, callback_data):
        keyboard.add(InlineKeyboardButton(txt, callback_data=id))
    bot.send_message(message.chat.id, msg_to_ask, reply_markup=keyboard)
