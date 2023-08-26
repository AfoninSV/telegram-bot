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
from database.core import db_interface


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

# Used before deployed on server to update list (takes long time so separated from server)
# INGREDIENS = [ingr for ingr in api.get_list_by_key(Factors.ingredients)
#               if api.search_by_ingredients(ingr)]
# with open("ingredients.txt", "w") as f:
#     f.write(", ".join(INGREDIENS))

# used to have list of categories in handlers file
CATEGORIES = api.get_list_by_key(Factors.categories)
AREAS = api.get_list_by_key(Factors.areas)
with open("ingredients.txt", "r") as f:
    INGREDIENTS = f.read().split(", ")


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
            f"\n{meal['ingredients_qty']} ingredients\n",
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
    """
    Retrieves the recipe for a given meal ID and returns the recipe picture, text and meal id.
    Writes meal data to db_meal
    """

    meal_id = meal_id or meal.get("idMeal")
    meal = meal or api.get_meal_by_id(meal_id)

    ingredients_str = api.get_meal_ingredients(meal_id).strip()
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

    return meal.get("strMealThumb"), reply_str, meal_id


def send_recipe_str(
    recipe_picture_link: str, recipe_str: str, meal_id: str, message: Message
) -> None:
    """Sends provided recipe in structured way with "favorite" button"""

    bot.send_photo(message.chat.id, recipe_picture_link)

    # check if string is longer that 4k symbols
    if is_favorite(message, meal_id=meal_id):
        if len(recipe_str) > 4096:  # TODO delete this and switch to telegra.ph
            recipe_str_1 = recipe_str[: recipe_str // 2]
            recipe_str_2 = recipe_str_1[recipe_str // 2 + 1 :]
            bot.send_message(message.chat.id, recipe_str_1)
            reply_markup(message, recipe_str_2, ["remove"], [f"delete|{meal_id}"])
        else:
            reply_markup(message, recipe_str, ["remove"], [f"delete|{meal_id}"])
    else:
        if len(recipe_str) > 4096:
            recipe_str_1 = recipe_str[: recipe_str // 2]
            recipe_str_2 = recipe_str_1[recipe_str // 2 + 1 :]
            bot.send_message(message.chat.id, recipe_str_1)
            reply_markup(message, recipe_str_2, ["add to favorites"], [f"add|{meal_id}"])
        else:
            reply_markup(message, recipe_str, ["add to favorites"], [f"add|{meal_id}"])


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
                if meals and len(meals) >= 3:
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
    """Send markup of user's favorite meals"""

    uid = message.from_user.id
    user_record = db_interface.read_by("User", "user_id", uid, as_dict=False)

    # Collect favorites meal ids and titles
    meal_ids = list()
    meal_titles = list()
    for record in user_record.favorites:
        meal_ids.append(record.meal.meal_id)
        meal_titles.append(record.meal.title)

    if meal_titles:
        reply_markup(message, "Favorite meals:", meal_titles, meal_ids)
    else:
        bot.send_message(message.chat.id, "Favorites list is empty")


def add_favorites(message: Message, meal_id: str):
    """Adds meal id and title to user's db"""

    uid: int = message.from_user.id
    cid: int = message.chat.id

    # Collect user and meal records from databases
    meal_record = db_interface.read_by("Meal", "meal_id", meal_id, as_dict=False)
    user_record = db_interface.read_by("User", "user_id", uid, as_dict=False)
    if not user_record:
        db_interface.insert("User", user_id=uid)
        user_record = db_interface.read_by("User", "user_id", uid, as_dict=False)

    # Insert relation to db if not exist
    if not is_favorite(message, meal_id):
        db_interface.insert("Favorites", user=user_record, meal=meal_record)
        bot.send_message(cid, f"Meal was added to your list.")
    else:
        bot.send_message(cid, f"This meal is already in your list.")


def delete_favorite(message: Message, meal_id: str) -> None:
    """Deletes relation of favorite meal from db"""

    uid = message.from_user.id
    cid: int = message.chat.id

    # Retrieve record of favorited meal from db
    favorite_meal_record = db_interface.read_by_multi("Favorites", user_id=uid, meal_id=meal_id)

    db_interface.delete("Favorites", favorite_meal_record.id)

    bot.send_message(cid, "Meal was deleted from your list")


def is_favorite(
    message: Message, meal_id: Optional[str] = None) -> bool:
    """Check if given meal id is in favorite list"""

    uid = message.from_user.id

    # Check if user exists in db
    if not db_interface.read_by("User", "user_id", uid, as_dict=False):
        db_interface.insert("User", user_id=uid)

    user_record = db_interface.read_by("User", "user_id", uid, as_dict=False)

    # Return if meal_id exists in user's favorite meals id list
    return meal_id in [record.meal.meal_id for record in user_record.favorites]
