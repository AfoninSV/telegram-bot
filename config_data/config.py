import os
from pathlib import Path

from dotenv import load_dotenv, find_dotenv
from pydantic import SecretStr, StrictStr, BaseSettings


if not find_dotenv():
    exit("No '.env' file found.")

env_path = Path(__file__).parent.parent.joinpath(".env")
load_dotenv(env_path)


class SettingsApi(BaseSettings):
    meal_api_key: SecretStr = os.getenv("API_KEY", None)
    meal_api_host: StrictStr = os.getenv("API_HOST", None)
    tg_token: SecretStr = os.getenv("TG_TOKEN")


api_settings = SettingsApi()
