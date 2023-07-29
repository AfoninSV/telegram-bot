from telebot.types import BotCommand


DEFAULT_COMMANDS = (
    ("/start", "Welcome"),
    ("/help", "Options"),
    ("/favorites", "Favorite meals"),
    ("/low", "Low ingredients"),
    ("/high", "Complex recipes"),
    ("/custom", "Specific ingredient range"),
    ("/random", "Random suggestion"),
    ("/search", "By ingredient or name"),
    ("/list", "Categories, areas, or ingredients"),
    ("/history", "Last ten queries"),
    ("/cancel", "Cancel operation")
)


def set_commands(bot):
    bot.set_my_commands([BotCommand(name, desc) for name, desc in DEFAULT_COMMANDS])
