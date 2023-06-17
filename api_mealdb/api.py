from config_data.config import api_settings
from utils.helpers import my_zip
from database.core import meal_interface
from typing import Optional, Dict
import requests


headers = {
    "X-RapidAPI-Key": api_settings.meal_api_key.get_secret_value(),
    "X-RapidAPI-Host": api_settings.meal_api_host
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
    response: dict = make_response("lookup", params=querystring)[0]
    return response


def get_meal_ingredients(meal_id) -> str:
    """Returns meal ingredients by id"""

    if meal := meal_interface.read_by("meal_id", meal_id):
        return meal.get("ingredients")

    meal = get_meal_by_id(meal_id)
    ingredients: list = [meal.get(f"strIngredient{ingredient_num}") for ingredient_num in range(1, 21)]
    measures = [meal.get(f"strMeasure{ingredient_num}") for ingredient_num in range(1, 21)]

    ingredient_list: str = "\n".join([f"{ingr} {meas}" for ingr, meas in my_zip(ingredients, measures)])
    meal_interface.insert(meal_id=meal_id, ingredients=ingredient_list)

    return ingredient_list


def meals_by_qty(category_name) -> list:
    """
    Returns list of meals by ingredients quantity by category.
    Base function to work with /low, /high commands
    """

    # Get list of meals id
    meals_list: list = get_meals_by_category(category_name)
    # Check if exists
    if meals_list is None:
        return

    # Loop through list of meaL id
    for meal in meals_list:
        # Get ID from meal dict
        meal_id = meal.get("idMeal")
        # Get ingredients of meal
        ingredients_list = get_meal_ingredients(meal_id)
        # Get len of ingredients list
        ingredients_qty = len(ingredients_list.split("\n"))
        # Write quantity to meal dictionary
        meal["ingredients_qty"] = ingredients_qty

    # Sort meals by their ingredients qty
    meals_list.sort(key=lambda meal: meal.get("ingredients_qty"))
    return meals_list


def low(category_name: str) -> Optional[list]:
    result = meals_by_qty(category_name)

    # Check for proper, existed reply
    if result is not None:
        return result[:3]


def high(category_name: str) -> Optional[list]:
    result = meals_by_qty(category_name)

    # Check for proper, existed reply
    if result is not None:
        return result[:-4:-1]
