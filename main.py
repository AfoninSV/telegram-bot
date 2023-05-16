from utils.helpers import config
from telegram_bot.handlers import start_handler
from telegram.ext import ApplicationBuilder

# Initialisation bot app
application = ApplicationBuilder().token(config.get('TG_TOKEN')).build()

# Add handlers to app
application.add_handler(start_handler)

# Run the app
application.run_polling()
