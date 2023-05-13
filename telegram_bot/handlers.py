import commands
from utils.helpers import config
from telegram.ext import ApplicationBuilder, CommandHandler


if __name__ == '__main__':
    application = ApplicationBuilder().token(config.get('TG_TOKEN')).build()

    start_handler = CommandHandler('start', commands.start)
    application.add_handler(start_handler)
    application.run_polling()
