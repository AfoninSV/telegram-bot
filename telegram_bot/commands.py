#from api_mealdb import api
#from database.core import history_interface





# def ask_category() -> int:
#     """Send message asking to input desired category"""
#
#     update.message.reply_text('Please enter the category name:')
#     # core.db_insert(update.message.text) WIP
#     if update.message.text == "/low":
#         return 1
#     elif update.message.text == "/high":
#         return 2
#     return 0
#
#
# def category_not_found() -> None:
#     """Sends message informing that looked database wasn't found and
#     sends existed fields"""
#     update.message.reply_text('Category not found, please see categories below and try again:')
#     categories_str = ", ".join(api.get_list_by_key(ListFactors.categories))
#     update.message.reply_text(categories_str)
#
#
# def category_meals_found(result: list) -> None:
#     """Sends a list of meals within provided list and asks the user to choose a meal"""
#
#     keyboard = list()
#     for i_meal, meal in enumerate(result, start=1):
#         update.message.reply_photo(f"{meal.get('strMealThumb')}\n",
#                                          caption=f"{i_meal}: {meal['strMeal']}"
#                                                  f"\n    {meal['ingredients_qty']} ingredients\n")
#         keyboard.append(InlineKeyboardButton(str(i_meal), callback_data=meal.get("idMeal")))
#
#     reply_markup = InlineKeyboardMarkup([keyboard])
#     update.message.reply_text("Please choose meal to get recipe:", reply_markup=reply_markup)
#
#
# def low_reply() -> int:
#     """Processes the user input for a category and searches based on the category name.
#     Used fod /low command."""
#
#     history_interface.insert(message=update.message.text)
#     update.message.reply_text('Searching...')
#     category_name = update.message.text
#     result = api.low(category_name)
#
#     if result is None:
#         category_not_found()
#         return 1
#
#     category_meals_found(, result)
#     return 3
#
#
# def high_reply() -> int:
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
#
#
# def cancel() -> None:
#     """Send notification that operation was canceled"""
#     update.message.reply_text('Operation cancelled.')
#
#
# def reply_recipe(meal_id) -> tuple:
#     """Retrieves the recipe for a given meal ID and returns the recipe picture and text"""
#
#     meal = api.get_meal_by_id(meal_id)
#     reply_str = str()
#
#     ingredients_str = api.get_meal_ingredients(meal_id).strip()
#     link = meal.get('strYoutube')
#
#     reply_str += f"Name: {meal.get('strMeal')}\n" \
#                  f"Category: {meal.get('strCategory')}\n" \
#                  f"Area: {meal.get('strArea')}\n" \
#                  f"Ingredients: {ingredients_str}" \
#                  f"\n\nInstruction:\n {meal.get('strInstructions')}\n" \
#                  f"{link}"
#
#     return meal.get("strMealThumb"), reply_str
#
#
# def button(update: : ContextTypes.DEFAULT_TYPE) -> int:
#     """Handles the button callback query, retrieves the chosen recipe, and sends the recipe details"""
#     query = update.callback_query
#     query.answer()
#
#     chosen_id = query.data
#
#     recipe_picture, recipe_text = reply_recipe(chosen_id)
#     query.message.reply_photo(recipe_picture)
#     query .message.reply_text(recipe_text)
#
#     return ConversationHandler.END
