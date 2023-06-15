from utils.helpers import start_message, ListFactors
from api_mealdb import api as am
from data.core import history_interface
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackContext, ConversationHandler


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends message with commands and instructions"""
    await context.bot.send_message(chat_id=update.effective_chat.id, text=start_message)


async def ask_category(update: Update, context) -> int:
    """Send message asking to input desired category"""

    await update.message.reply_text('Please enter the category name:')
    # core.db_insert(update.message.text) WIP
    if update.message.text == "/low":
        return 1
    elif update.message.text == "/high":
        return 2
    return 0


async def category_not_found(update: Update, context: CallbackContext) -> None:
    """Sends message informing that looked data wasn't found and
    sends existed fields"""
    await update.message.reply_text('Category not found, please see categories below and try again:')
    categories_str = ", ".join(am.get_list_by_key(ListFactors.categories))
    await update.message.reply_text(categories_str)


async def category_meals_found(update: Update, context: CallbackContext, result: list) -> None:
    """Sends a list of meals within provided list and asks the user to choose a meal"""

    keyboard = list()
    for i_meal, meal in enumerate(result, start=1):
        await update.message.reply_photo(f"{meal.get('strMealThumb')}\n",
                                         caption=f"{i_meal}: {meal['strMeal']}"
                                                 f"\n    {meal['ingredients_qty']} ingredients\n")
        keyboard.append(InlineKeyboardButton(str(i_meal), callback_data=meal.get("idMeal")))

    reply_markup = InlineKeyboardMarkup([keyboard])
    await update.message.reply_text("Please choose meal to get recipe:", reply_markup=reply_markup)


async def low_reply(update: Update, context: CallbackContext) -> int:
    """Processes the user input for a category and searches based on the category name.
    Used fod /low command."""

    history_interface.insert(message=update.message.text)
    await update.message.reply_text('Searching...')
    category_name = update.message.text
    result = am.low(category_name)

    if result is None:
        await category_not_found(update, context)
        return 1

    await category_meals_found(update, context, result)
    return 3


async def high_reply(update: Update, context: CallbackContext) -> int:
    """Processes the user input for a category and searches based on the category name.
    Used fod /high command."""

    history_interface.insert(message=update.message.text)
    await update.message.reply_text('Searching...')
    category_name = update.message.text
    result = am.high(category_name)

    if result is None:
        await category_not_found(update, context)
        return 2

    await category_meals_found(update, context, result)
    return 3


async def cancel(update: Update, context: CallbackContext) -> None:
    """Send notification that operation was canceled"""
    await update.message.reply_text('Operation cancelled.')


def reply_recipe(meal_id) -> tuple:
    """Retrieves the recipe for a given meal ID and returns the recipe picture and text"""

    meal = am.get_meal_by_id(meal_id)
    reply_str = str()

    ingredients_str = am.get_meal_ingredients(meal_id).strip()
    link = meal.get('strYoutube')

    reply_str += f"Name: {meal.get('strMeal')}\n" \
                 f"Category: {meal.get('strCategory')}\n" \
                 f"Area: {meal.get('strArea')}\n" \
                 f"Ingredients: {ingredients_str}" \
                 f"\n\nInstruction:\n {meal.get('strInstructions')}\n" \
                 f"{link}"

    return meal.get("strMealThumb"), reply_str


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles the button callback query, retrieves the chosen recipe, and sends the recipe details"""
    query = update.callback_query
    await query.answer()

    chosen_id = query.data

    recipe_picture, recipe_text = reply_recipe(chosen_id)
    await query.message.reply_photo(recipe_picture)
    await query .message.reply_text(recipe_text)

    return ConversationHandler.END
