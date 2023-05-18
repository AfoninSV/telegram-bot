from utils.helpers import SettingsApi
import requests

api_sets = SettingsApi()

headers = {
    "X-RapidAPI-Key": api_sets.api_key.get_secret_value(),
    "X-RapidAPI-Host": api_sets.api_host
}


def get_list_response(list_factor: str) -> list[dict]:
    """Returns list of categories/area/ingredients accordingly to given factor"""

    url = f"https://themealdb.p.rapidapi.com/list.php"
    querystring = {list_factor: "list"}

    response: dict = requests.get(url, headers=headers, params=querystring).json().get("meals")
    if not response:
        # Log returned None from api server
        ...
    return response
