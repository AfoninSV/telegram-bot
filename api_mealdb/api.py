from utils.helpers import SettingsApi
from typing import Optional, Dict
import requests

api_sets = SettingsApi()

headers = {
    "X-RapidAPI-Key": api_sets.api_key.get_secret_value(),
    "X-RapidAPI-Host": api_sets.api_host
}


def make_response(action: str, headers: Dict[str, str]=headers, params: Optional[Dict] = None) -> list:
    url = f"https://themealdb.p.rapidapi.com/{action}.php"
    response = requests.get(url, headers=headers, params=params).json().get("meals")
    return response


def get_list_response(list_factor: str) -> list:
    """Returns list of categories/area/ingredients accordingly to given factor"""

    querystring = {list_factor: "list"}

    response: list = make_response("list", params=querystring)

    # Open list[dict] to list[dict_value]
    items_names = [list(item.values())[0] for item in response]
    return items_names
