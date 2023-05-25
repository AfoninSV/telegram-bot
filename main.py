from utils.helpers import api_sets
from telegram_bot.handlers import start_handler
from telegram.ext import ApplicationBuilder

# Initialisation bot app
application = ApplicationBuilder().token(api_sets.tg_token.get_secret_value()).build()

# Add handlers to app
application.add_handler(start_handler)

# Run the app
application.run_polling()
