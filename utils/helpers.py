from dataclasses import dataclass
from database.core import history_interface, History


@dataclass
class ListFactors:
    categories: str = "c"
    area: str = "a"
    ingredients: str = "i"


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

    query = History.select().where(History.user_id == user_id).order_by(History.id_key.desc())
    last_n_records = list(query)

    if len(last_n_records) > 20:
        records_to_delete = last_n_records[:-20]  # Exclude the last 20 records
        delete_query = History.delete().where(History.id_key.in_(records_to_delete))
        delete_query.execute()


def get_last_n_from_history(n: int, user_id: str):
    db = history_interface
    values = db.read_all()
    sorted_values = [row.message for row in values if row.user_id == user_id]
    history_clean(user_id)

    if len(sorted_values) >= n:
        return sorted_values[-n]
    return sorted_values[-len(sorted_values)]


start_message = """
Welcome to the Telegram Recipe Bot!

Our bot helps you discover various cooking recipes. 
Whether you want something simple or more challenging, we've got you covered.

Here are the core commands our bot supports:

- /low: Find easy recipes based on the number of ingredients. Specify a dish type (e.g., "dessert" or "main course") to get simple recipes in that category.
- /high: Get complex recipes with more ingredients. Test your skills with these challenging dishes.
- /custom: Specify a range of ingredients, and the bot will find recipes within that range.
- /random: Discover new recipes with a random suggestion.
- /search: Find recipes that include a specific ingredient or by name.
- /list: Get a list of all categories, areas, and ingredients.
- /history: See your last ten queries, including the command type, parameters used, and query time.

Happy cooking!
"""
