import os
from pathlib import Path
from dataclasses import dataclass
from dotenv import load_dotenv
from pydantic import SecretStr, StrictStr, BaseSettings


env_path = Path(__file__).parent.parent.joinpath(".env")
load_dotenv(env_path)


class SettingsApi(BaseSettings):
    api_key: SecretStr = os.getenv("API_KEY", None)
    api_host: StrictStr = os.getenv("API_HOST", None)
    tg_token: SecretStr = os.getenv("TG_TOKEN")


api_sets = SettingsApi()


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

