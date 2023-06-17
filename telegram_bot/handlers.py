from utils.helpers import start_message
from loader import bot


@bot.message_handler(commands=['start', 'help'])
def send_start(message) -> None:
    """Sends message with commands and instructions"""
    bot.send_message(message.chat.id, start_message)
