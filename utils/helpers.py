import os
from dotenv import dotenv_values

# Load environment values
config: dict = dotenv_values(os.path.join("..", ".env"))
