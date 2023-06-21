from api_mealdb import api
from loader import bot
from utils.helpers import ListFactors, get_last_n_from_history
from database.core import history_interface, states_interface
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from telebot.callback_data import CallbackData, CallbackDataFilter
from telebot.custom_filters import AdvancedCustomFilter

"""
states:
    0: cancel,
    1: ask_category,
    2: low_reply,
    3: high_reply,
    4: button
"""

products_factory = CallbackData('meal_id', prefix='meals')

def get_user_state(msg: Message):
    result = states_interface.read_by("user_id", msg.from_user.id)
    if result:
        return result.get('state')
    return None


def set_user_state(msg: Message, state: int) -> None:
    if get_user_state(msg) is None:
        states_interface.insert(user_id=msg.from_user.id, state=state)
    else:
        states_interface.update('state', state, user_id=msg.from_user.id)


def get_last_user_msg(message):
    history_interface.read_by('user_id', message.from_user.id)


def ask_category(message) -> int:
    """Send message asking to input desired category"""

    last_cmd = get_last_n_from_history(1, message.from_user.id)
    bot.send_message(message.chat.id, 'Please enter the category name:')

    if last_cmd == '/low':
        history_interface.insert(user_id=message.from_user.id, message='/low')
        set_user_state(message, 2)
        return 2
    elif last_cmd == '/high':
        history_interface.insert(user_id=message.from_user.id, message='/high')
        set_user_state(message, 3)
        return 3


def category_not_found(message: Message) -> None:
    """Sends message informing that looked database wasn't found and
    sends existed fields"""

    categories_str = ", ".join(api.get_list_by_key(ListFactors.categories))
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
                                      callback_data=products_factory.new(meal_id=meal.get('idMeal')))
        keyboard.add(button)

    bot.send_message(message.chat.id, "Please choose meal to get recipe:", reply_markup=keyboard)
    set_user_state(message, 0)
    # bot.register_next_step_handler_by_chat_id(message.chat.id, states.states[0])


def low_reply(message: Message) -> None:
    """Processes the user input for a category and searches based on the category name.
    Used fod /low command."""

    bot.send_message(message.chat.id, 'Searching...')
    category_name = message.text
    result = api.low(category_name)

    if result is None:
        category_not_found(message)
        # bot.register_next_step_handler_by_chat_id(message.chat.id, states.states[2])
    else:
        category_meals_found(message, result)
        set_user_state(message, 4)
        # bot.register_next_step_handler_by_chat_id(message.chat.id, states.states[4])


def high_reply(message: Message) -> int:
    ...
#     """Processes the user input for a category and searches based on the category name.
#     Used fod /high command."""
#
#     history_interface.insert(message=update.message.text)
#     update.message.reply_text('Searching...')
#     category_name = update.message.text
#     result = api.high(category_name)
#
#     if result is None:
#         category_not_found()
#         return 2
#
#     category_meals_found(, result)
#     return 3


def cancel(message: Message) -> None:
    """Send notification that operation was canceled"""
    bot.send_message(message.chat.id, 'Operation cancelled.')


def reply_recipe(meal_id) -> tuple:
    """Retrieves the recipe for a given meal ID and returns the recipe picture and text"""

    meal = api.get_meal_by_id(meal_id)
    reply_str = str()

    ingredients_str = api.get_meal_ingredients(meal_id).strip()
    link = meal.get('strYoutube')

    reply_str += f"Name: {meal.get('strMeal')}\n" \
                 f"Category: {meal.get('strCategory')}\n" \
                 f"Area: {meal.get('strArea')}\n" \
                 f"Ingredients: {ingredients_str}" \
                 f"\n\nInstruction:\n {meal.get('strInstructions')}\n" \
                 f"{link}"

    return meal.get("strMealThumb"), reply_str


@bot.callback_query_handler(lambda call: True)
def button(call) -> int:
    """Handles the button callback query, retrieves the chosen recipe, and sends the recipe details"""

    callback_data: dict =   products_factory.parse(call.data)

    chosen_id = callback_data.get('meal_id')
    print(callback_data, type(callback_data))
    print(chosen_id)

    recipe_picture, recipe_text = reply_recipe(chosen_id)
    bot.send_photo(call.message.chat.id, recipe_picture)
    bot.send_message(call.message.chat.id, recipe_text)
