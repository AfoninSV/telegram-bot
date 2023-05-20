from utils.helpers import SettingsApi, my_zip
from typing import Optional, Dict
import requests
from pprint import pprint

api_sets = SettingsApi()

headers = {
    "X-RapidAPI-Key": api_sets.api_key.get_secret_value(),
    "X-RapidAPI-Host": api_sets.api_host
}


def make_response(url_action: str, headers: Dict[str, str]=headers, params: Optional[Dict] = None) -> list:
    url = f"https://themealdb.p.rapidapi.com/{url_action}.php"
    response = requests.get(url, headers=headers, params=params).json().get("meals")
    return response


def get_list_by_key(list_factor: str) -> list:
    """Returns list of categories/area/ingredients accordingly to given factor"""

    querystring = {list_factor: "list"}

    response: list = make_response("list", params=querystring)

    # Open list[dict] to list[dict_value]
    items_names = [list(item.values())[0] for item in response]
    return items_names


def get_meal_by_name(meal_name: str) -> Optional[dict]:
    """Returns list of meals by name or None"""

    querystring = {"s": meal_name}
    response: list[dict] = make_response("search", params=querystring)
    if response is None:
        return

    response: dict[int, dict] = {item[0]: item[1] for item in enumerate(response, start=1)}

    return response


def get_random_meal() -> dict:
    """Returns random meal dict"""

    return make_response("random")[0]


def get_meals_by_category(category_name) -> list[dict]:
    """Returns meals list by given category"""

    querystring = {"c": category_name}
    response: list[dict] = make_response("filter", params=querystring)
    return response


def get_meal_by_id(meal_id) -> dict:
    """Returns meal's description by id"""

    querystring = {"i": str(meal_id)}
    response: list = make_response("lookup", params=querystring)
    return response[0]


def get_meal_ingredients(meal_id) -> list[tuple]:
    """Returns meal ingredients by id"""

    meal = get_meal_by_id(meal_id)
    ingredients: list = [meal.get(f"strIngredient{ingredient_num}") for ingredient_num in range(1, 21)]
    measures = [meal.get(f"strMeasure{ingredient_num}") for ingredient_num in range(1, 21)]

    return my_zip(ingredients, measures)


def low(category_name):
    """
    Returns slice of first 3 meals
    with the lowest quantity of ingredients by category
    """

    meals_list = get_meals_by_category(category_name)

    for meal in meals_list:
        meal_id = meal.get("idMeal")
        ingredients_list = get_meal_ingredients(meal_id)
        ingredients_qty = len(ingredients_list)
        meal["ingredients_qty"] = ingredients_qty

    meals_list.sort(key=lambda meal: meal.get("ingredients_qty"))
    return meals_list[:3]


if __name__ == "__main__":
    pprint(get_meals_by_category("pork"))
    pprint(get_meal_by_id(52885))
    pprint(get_meal_ingredients(52885))
    pprint(low("pork"))