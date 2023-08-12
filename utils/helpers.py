from dataclasses import dataclass

from database.core import history_interface


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


def history_clean(user_id) -> None:
    """Deletes rows of History table if there are more than 20 for asked user id"""

    db = history_interface
    values = db.read_all("History")
    sorted_values = [row for row in values if row.user_id == user_id]

    if len(sorted_values) > 20:
        records_to_delete = sorted_values[:-20]
        for record in records_to_delete:
            db.delete("History", record.id)


def get_last_n_from_history(n: int, user_id: int) -> list[tuple] | None:
    n = n + 1
    db = history_interface
    values = db.read_all("History")

    sorted_values = [
        row.message for row in values if row.user_id == user_id
    ]
    history_clean(user_id)

    if sorted_values:
        if len(sorted_values) >= n:
            return sorted_values[:-n:-1]
        else:
            return sorted_values


start_message = """
Hey hey, welcome to the Telegram Recipe Bot!

I'm here to assist you in discovering cooking recipes, whether you're after simple dishes or a culinary journey – I'm here for you. 
Just type /help to see the available options and what they're all about.

Have a blast cooking up a storm!
"""


help_message = """
Here are the core commands:

- /low: Search for easy recipes based on ingredient count.
- /high: Challenge yourself with complex recipes having more ingredients.
- /custom: Set a range of ingredients, and I will find recipes within that range.
- /random: Explore fresh recipes with a random suggestion.
- /search: Find recipes by a specific ingredient or name.
- /list: Get a list of categories, areas, or ingredients.
- /favorites: Check out your saved recipes.
- /history: Review your last ten queries.
- /cancel: Stop ongoing operations (or just use another command).

Feel free to give these commands a try and have fun in your cooking adventures! 
"""
