from telebot.types import BotCommand


DEFAULT_COMMANDS = (
    ("/start", "Welcome message"),
    ("/help", "Available options"),
    ("/low", "Recipes with low ingredients"),
    ("/high", "Complex recipes with more ingredients"),
    ("/custom", "Find recipes within a specified ingredient range"),
    ("/random", "Discover new recipes with a random suggestion"),
    ("/search", "Find recipes by ingredient or name"),
    ("/list", "Get a list of categories, areas, or ingredients"),
    ("/history", "See your last ten queries"),
    ("/cancel", "Cancel the current operation or use another command")
)


def set_commands(bot):
    bot.set_my_commands([BotCommand(name, desc) for name, desc in DEFAULT_COMMANDS])
