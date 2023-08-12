from telebot.types import BotCommand


DEFAULT_COMMANDS = (
    ("/help", "Options"),
    ("/search", "Search by ingredient or name"),
    ("/random", "Random meal suggestion"),
    ("/favorites", "Favorite meals"),
    ("/low", "Low ingredients"),
    ("/high", "Complex recipes"),
    ("/custom", "Specific ingredient range"),


    ("/list", "Categories, areas, or ingredients"),
    ("/history", "Last ten queries"),
    ("/cancel", "Cancel operation"),
)


def set_commands(bot):
    bot.set_my_commands([BotCommand(name, desc) for name, desc in DEFAULT_COMMANDS])
