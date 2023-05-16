from pathlib import Path
from dotenv import dotenv_values

env_path = Path(__file__).parent.parent.joinpath(".env")

# Load environment values
config: dict = dotenv_values(env_path)

start_message = """
Welcome to the Telegram Recipe Bot!

Our bot helps you discover various cooking recipes. 
Whether you want something simple or more challenging, we've got you covered.

Here are the core commands our bot supports:

- /low: Find easy recipes based on the number of ingredients. Specify a dish type (e.g., "dessert" or "main course") to get simple recipes in that category.
- /high: Get complex recipes with more ingredients. Test your skills with these challenging dishes.
- /custom: Specify a range of ingredients, and the bot will find recipes within that range.
- /random: Discover new recipes with a random suggestion.
- /search: Find recipes that include a specific ingredient.
- /list: Get a list of all categories, areas, and ingredients.
- /history: See your last ten queries, including the command type, parameters used, and query time.

Happy cooking!
"""

