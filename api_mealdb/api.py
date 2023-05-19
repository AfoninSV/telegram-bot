from utils.helpers import SettingsApi
from typing import Optional, Dict
import requests
from pprint import pprint

api_sets = SettingsApi()

headers = {
    "X-RapidAPI-Key": api_sets.api_key.get_secret_value(),
    "X-RapidAPI-Host": api_sets.api_host
}


def make_response(action: str, headers: Dict[str, str]=headers, params: Optional[Dict] = None) -> list:
    url = f"https://themealdb.p.rapidapi.com/{action}.php"
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
    return make_response("random")[0]

pprint(get_random_meal())
