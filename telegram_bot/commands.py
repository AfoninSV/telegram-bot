from typing import Optional
from string import ascii_lowercase
from itertools import combinations
import re
import json

from telebot.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from api_mealdb import api
from loader import bot, storage
from utils.helpers import Factors, get_last_n_from_history
from .states import ConversationStates, set_user_state
from database.core import history_interface, fridge_interface, favorites_interface

"""
states:
    cancel: cancel (waiting),
    wait_button: button_reply
    wait_range: custom command
    wait_random: wait for random
    wait_name: wait for meal name
    wait_ingredients: wait for ingredients
    list_reply: ask for list type
"""

# TODO move everything not used in handlers to separate file!
#

# used to have list of categories in handlers file
CATEGORIES = api.get_list_by_key(Factors.categories)
AREAS = api.get_list_by_key(Factors.areas)
with open("ingredients.txt", "r") as f:
    INGREDIENTS = f.read().split(", ")

# TODO change the way ingredients are saved (.txt file? cmon)

# Used before deployed on server to update list (takes long time so separated from server)
# INGREDIENS = [ingr for ingr in api.get_list_by_key(Factors.ingredients)
#               if api.search_by_ingredients(ingr)]


def reply_markup(
    message,
    msg_to_ask: str,
    button_text: list = None,
    callback_data: list = None,
    meals_list=None,
) -> None:
    """Sends message with keyboard markup with given data"""

    keyboard = InlineKeyboardMarkup()
    if meals_list:
        button_text = list()
        callback_data = list()
        for meal in meals_list:
            button_text.append(meal.get("strMeal"))
            callback_data.append(meal.get("idMeal"))

    for txt, id in zip(button_text, callback_data):
        keyboard.add(InlineKeyboardButton(txt, callback_data=id))
    bot.send_message(message.chat.id, msg_to_ask, reply_markup=keyboard)


def ask_category(message) -> None:
    """Send message asking to input desired category"""

    last_command = get_last_n_from_history(1, message.from_user.id)[0][1]

    categories_str = ", ".join(CATEGORIES)
    reply_markup(message, "Available categories:", CATEGORIES, CATEGORIES)
    set_user_state(message, ConversationStates.wait_button)


def category_not_found(message: Message) -> None:
    """Sends message informing that looked database wasn't found and
    sends existed fields"""

    categories_str = ", ".join(CATEGORIES)
    bot.send_message(
        message.chat.id,
        f"Category not found, please see categories below: " f"\n\n{categories_str}",
    )
    bot.send_message(message.chat.id, "Try again: ")


def category_meals_found(message: Message, result: list) -> int:
    """Sends a list of meals within provided list and asks the user to choose a meal"""

    keyboard = InlineKeyboardMarkup()
    for i_meal, meal in enumerate(result, start=1):
        bot.send_photo(
            message.chat.id,
            f"{meal.get('strMealThumb')}\n",
            caption=f"{i_meal}: {meal['strMeal']}"
            f"\n    {meal['ingredients_qty']} ingredients\n",
        )
        button = InlineKeyboardButton(text=i_meal, callback_data=meal.get("idMeal"))
        keyboard.add(button)

    bot.send_message(
        message.chat.id, "Please choose meal to get recipe:", reply_markup=keyboard
    )
    set_user_state(message, ConversationStates.cancel)


def low_high_reply(call: CallbackQuery, func=api.low) -> None:
    """Base function for low_reply, high_reply.
    Processes the user input for a category and searches based on the category name.
    Used for /low and /high commands."""

    message = call.message

    bot.send_message(message.chat.id, "Searching...")
    category_name = call.data
    result = func(category_name)

    if result is None:
        category_not_found(message)
    else:
        category_meals_found(message, result)


def low_reply(call: CallbackQuery) -> None:
    low_high_reply(call)


def high_reply(call: CallbackQuery) -> None:
    low_high_reply(call, func=api.high)


def cancel(message: Message) -> None:
    """Send notification that operation was canceled"""
    bot.send_message(message.chat.id, "Operation cancelled.")


def get_recipe_str(
    meal_id: Optional[str] = None, meal: Optional[dict] = None
) -> tuple[str]:
    """Retrieves the recipe for a given meal ID and returns the recipe picture and text"""

    if meal_id:
        meal = api.get_meal_by_id(meal_id)

        ingredients_str = api.get_meal_ingredients(meal_id).strip()
        link = meal.get("strYoutube")
    else:
        ingredients_str = api.get_meal_ingredients(meal.get("idMeal")).strip()
        link = meal.get("strYoutube")

    reply_str = str()
    reply_str += (
        f"Name: {meal.get('strMeal')}\n"
        f"Category: {meal.get('strCategory')}\n"
        f"Area: {meal.get('strArea')}\n\n"
        f"Ingredients: \n{ingredients_str}\n\n"
        f"Instruction:\n {meal.get('strInstructions')}\n"
        f"{link}"
    )
    # used as callback data for buttons to work with favorites list
    favorites_data = {"id": meal.get("idMeal"), "title": meal.get("strMeal")}
    return meal.get("strMealThumb"), reply_str, json.dumps(favorites_data)


def send_recipe_str(
    recipe_picture: str, recipe_str: str, favs_data: str, message: Message
) -> None:
    """
    Sends provided recipe in structured way with "favorite" button
    :param favs_data: '{"id":"meal id", "title": "meal title"}', json used
    """

    bot.send_photo(message.chat.id, recipe_picture)
    # check if string is longer that 4k symbols
    if is_favorite(message, favs_data=favs_data):
        if len(recipe_str) > 4096:  # TODO delete this and switch to telegra.ph
            recipe_str_1 = recipe_str[: recipe_str // 2]
            recipe_str_2 = recipe_str_1[recipe_str // 2 + 1 :]
            bot.send_message(message.chat.id, recipe_str_1)
            reply_markup(message, recipe_str_2, ["remove"], [f"delete|{favs_data}"])
        else:
            #bot.send_message(message.chat.id, recipe_str)
            reply_markup(message, recipe_str, ["remove"], [f"delete|{favs_data}"])
    else:
        if len(recipe_str) > 4096:
            recipe_str_1 = recipe_str[: recipe_str // 2]
            recipe_str_2 = recipe_str_1[recipe_str // 2 + 1 :]
            bot.send_message(message.chat.id, recipe_str_1)
            reply_markup(message, recipe_str_2, ["add to favorites"], [f"add|{favs_data}"])
        else:
            reply_markup(message, recipe_str, ["add to favorites"], [f"add|{favs_data}"])


def meal_id_button_get(call) -> None:
    """Handles the button callback query, retrieves the chosen recipe, and sends the recipe details"""

    chosen_id = call.data
    send_recipe_str(*get_recipe_str(meal_id=chosen_id), call.message)
    set_user_state(call.message, ConversationStates.cancel)


def ask_for(
    message: Message, ask_text: str, state: Optional[ConversationStates] = None
) -> None:
    bot.send_message(message.chat.id, ask_text)

    if state:
        set_user_state(message, state)


def check_range(range_str: str) -> bool | list:
    # check 'number, number'
    if match := re.match(r"\d+,\s*\d+", range_str):
        start, end = re.split(r",\s*", match.group(0))
        start = int(start)
        end = int(end)
        if end < start:
            return False
        if (start > 99) or (end <= 0) or (end > 99):
            return False
        if match.group(0) != range_str:
            return False
        return list(range(start, end + 1))

    # check 'number'
    if match := re.match(r"\d+", range_str):
        if match.group(0) != range_str:
            return False
        if (int(match.group(0)) > 99) or (int(match.group(0)) <= 0):
            return False
        return [int(match.group(0))]


def check_all_for_qty(qty_range: list) -> list[dict]:
    fit = list()
    for letter in ascii_lowercase:
        meals: list = api.meals_by_first_letter(letter)
        if meals:
            for meal in meals:
                if (qty := api.get_ingredients_qty(meal.get("idMeal"))) in qty_range:
                    fit.append(meal)
    return fit


def random_recipe(message: Message) -> None:
    random_recipe: dict = api.get_random_meal()
    send_recipe_str(*get_recipe_str(meal=random_recipe), message)
    set_user_state(message, ConversationStates.cancel)


def ask_for_list(message: Message) -> None:
    """Sends reply markup of [areas, categories, ingredients]"""

    types = {"areas", "categories", "ingredients"}
    reply_markup(message, "Please choose the type of desired list:", types, types)
    set_user_state(message, ConversationStates.cancel)


def list_reply(message: Message, factor: str) -> None:
    names_list = api.get_list_by_key(factor)
    callback_names = [f"filter {name}" for name in names_list]
    if factor == "a":
        reply_markup(
            message, "Choose to see meals of that area:", names_list, callback_names
        )
    elif factor == "c":
        reply_markup(
            message, "Choose to see meals of that category:", names_list, callback_names
        )
    elif factor == "i":
        # if len(names_str) > 4096:
        INGREDIENS = ", ".join(names_list)
        list_len = len(names_list)
        names_str_1 = ", ".join(names_list[: list_len // 2])
        names_str_2 = ", ".join(names_list[list_len // 2 + 1 :])

        bot.send_message(message.chat.id, names_str_1)
        bot.send_message(message.chat.id, names_str_2)
    else:
        bot.send_message(message.chat.id, names_str)
    set_user_state(message, ConversationStates.cancel)


def find_by_name(message: Message, name: str) -> None:
    if meals := api.get_meal_by_name(name):
        if len(meals) == 1:
            meal = meals[0]
            send_recipe_str(*get_recipe_str(meal=meal), message)
            set_user_state(message, ConversationStates.cancel)
        else:
            keyboard = InlineKeyboardMarkup()
            for meal in meals:
                meal_name = meal.get("strMeal")
                meal_id = meal.get("idMeal")
                keyboard.add(InlineKeyboardButton(meal_name, callback_data=meal_id))
            bot.send_message(
                message.chat.id, "Chose meal you want to see:", reply_markup=keyboard
            )

    else:
        bot.send_message(message.chat.id, "Nothing found, try again:")


def check_ingredients_list(message: Message) -> list:
    """Turns string list divided by commas with list of words,
    whitespaces are changed with _"""

    ingredients_string = message.text.strip()
    ingredients_list = re.split(r",\s*", ingredients_string.lower())
    ingredients_list = [
        re.sub(r"\s+", "_", name) if re.search(r"\s+", name) else name
        for name in ingredients_list
    ]
    return ingredients_list


def reply_search_by_ingredients(message: Message, ingredients_list: list):
    ingredients = ",".join(ingredients_list)
    meals: list = api.search_by_ingredients(ingredients)
    if not meals:
        bot.send_message(
            message.chat.id,
            "I couldn't find the exact ingredients list, "
            "but you may want to try these meals that use similar ingredients...",
        )
        meals = list()
        for minusable in range(1, len(ingredients_list)):
            for ingredients_list_tmp in combinations(ingredients_list, len(ingredients_list) - minusable):
                ingredients = ",".join(ingredients_list_tmp)
                meals_to_try: list = api.search_by_ingredients(ingredients)
                meals += meals_to_try or list()
                if len(meals) >= 3:
                    break
    if meals:
        reply_markup(
            message, "Select which meal would you like to see:", meals_list=meals
        )
        set_user_state(message, ConversationStates.cancel)
        return
    bot.send_message(message.chat.id, "Nothing found, try again:")


def reply_categories(message: Message, category: str) -> None:
    meals_list = api.get_meals_by_category(category)
    reply_markup(message, "Meals found:", meals_list=meals_list)


def reply_areas(message: Message, area: str) -> None:
    meals_list = api.get_meal_by_area(area)
    reply_markup(message, "Meals found:", meals_list=meals_list)


def show_favorites(message: Message):
    uid = message.from_user.id
    favs_data = favorites_interface.read_by("user_id", uid)
    if favs_data:
        favs_meals: list[dict] = json.loads(favs_data["meals"])
        callback_data = [meal["id"] for meal in favs_meals]
        meals_names = [meal["title"] for meal in favs_meals]
        reply_markup(message, "Your favorites:", meals_names, callback_data)
    else:
        bot.send_message(message.chat.id, "Your favorites list is empty")


def add_favorites(message: Message, favorites_data: str):
    """Adds meal id and title to user's db"""

    uid: int = message.from_user.id
    cid: int = message.chat.id
    data: dict = json.loads(favorites_data)

    db_row: dict = favorites_interface.read_by("user_id", uid)
    if db_row:
        saved_meals: list = json.loads(db_row["meals"])
        if data["id"] not in [meal["id"] for meal in saved_meals]:
            saved_meals.append(data)

            json_data: str = json.dumps(saved_meals)
            favorites_interface.update("meals", json_data, "user_id", uid)
            bot.send_message(cid, f"Meal was added to your list.")
        else:
            bot.send_message(cid, f"The meal is already in your list.")
    else:
        empty_list = []
        empty_list.append(data)
        json_data = json.dumps(empty_list)
        favorites_interface.insert(user_id=uid, meals=json_data, meals_id=data["id"])
        bot.send_message(cid, f"Meal was added to your list.")


def delete_favorite(message: Message, favs_data: str) -> None:
    uid = message.from_user.id
    cid: int = message.chat.id
    meal_id = json.loads(favs_data)["id"]

    # get user's data from favorites db
    db_row: dict = favorites_interface.read_by("user_id", uid)
    # get list of saved meals from db_row
    saved_meals: str = db_row["meals"]
    # deserializing saved meals list
    saved_meals: list[dict] = json.loads(saved_meals)
    meal_index: int = [i_meal
                       for i_meal, meal in enumerate(saved_meals)
                       if meal["id"] == meal_id][0]

    # remove meal from saved list
    saved_meals.pop(meal_index)
    # replase saved list with one in db
    favorites_interface.update("meals", json.dumps(saved_meals), "user_id", uid)

    bot.send_message(cid, "Meal was removed from your list")



def is_favorite(
    message: Message, meal_id: Optional[str] = None, favs_data: Optional[str] = None
) -> bool:
    """
    Check if given meal id is in favorite list or execute meal id from favs_data,
    at least any should be filled or False is returned
    """

    uid = message.from_user.id
    users_favs: dict = favorites_interface.read_by("user_id", uid)

    if not meal_id:
        if favs_data:
            meal_id = json.loads(favs_data)["id"]
        else:
            return False

    fav_meals_id = [meal["id"] for meal in json.loads(users_favs["meals"])]

    return meal_id in fav_meals_id
