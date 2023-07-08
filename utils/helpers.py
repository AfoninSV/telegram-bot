from dataclasses import dataclass

from database.core import history_interface, History


@dataclass
class Factors:
    categories: str = "c"
    areas: str = "a"
    ingredients: str = "i"
    search: str = "s"
    first_letter: str = "f"


def my_zip(list_ingr, list_measr) -> list[tuple]:
    """Zips list, avoiding empty strings"""

    # String of ingredients
    result_list = list()
    for item in zip(list_ingr, list_measr):
        # check for empty cell
        if item[0] is None or len(item[0]) == 0:
            return result_list

        result_list.append(item)
    return result_list


def history_clean(user_id):
    """Deletes rows of History table if there are more than 20 for asked user id"""

    db = history_interface
    values = db.read_all()
    sorted_values = [row for row in values if row.user_id == user_id]
    
    if len(sorted_values) > 20:
        records_to_delete = sorted_values[:-20]
        for record in records_to_delete:
            db.delete(record.id_key)


def get_last_n_from_history(n: int, user_id: int):
    n = n + 2
    db = history_interface
    values = db.read_all()
    
    sorted_values = [f'{row.date_time}: {row.message}' for row in values if row.user_id == user_id]
    history_clean(user_id)

    if sorted_values:
        if len(sorted_values) >= n:
            return sorted_values[-2:-n:-1]
    return 'History is empty.'


start_message = """
Welcome to the Telegram Recipe Bot!

Our bot helps you discover various cooking recipes. 
Whether you want something simple or more challenging, we've got you covered.

Happy cooking!
"""


help_message = """
Here are the core commands our bot supports:

- /low: Find easy recipes based on the number of ingredients. Specify a dish type (e.g., "dessert" or "main course") to get simple recipes in that category.
- /high: Get complex recipes with more ingredients. Test your skills with these challenging dishes.
- /custom: Specify a range of ingredients, and the bot will find recipes within that range.
- /random: Discover new recipes with a random suggestion.
- /search: Find recipes that include a specific ingredient or by name.
- /list: Get a list of all categories, areas, or ingredients.
- /history: See your last ten queries.
- /cancel: Cancel actual operation (or just use another command).
"""
