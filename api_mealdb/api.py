from utils import helpers
import requests


headers = {
    "X-RapidAPI-Key": helpers.config.get("API_KEY"),
    "X-RapidAPI-Host": "themealdb.p.rapidapi.com"
}
factors = {
    "categories": "c",
    "area": "a",
    "ingredients": "i"
}


def get_list(factor: str) -> list[str]:
    """Returns list of categories or area accordingly to given factor"""

    url = "https://themealdb.p.rapidapi.com/list.php"
    querystring = {factor: "list"}

    # get item names list from json dict
    response: dict = requests.get(url, headers=headers, params=querystring).json()
    response: list = [f"{category.get('strCategory').capitalize()}"
                      for category in response.get("meals")]

    return response
