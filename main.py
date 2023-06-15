from utils.helpers import api_sets
from telegram_bot.handlers import start_handler, lh_conversation
from telegram.ext import ApplicationBuilder

# Initialisation bot app
application = ApplicationBuilder().token(api_sets.tg_token.get_secret_value()).build()

# Add handlers to app
application.add_handler(start_handler)
application.add_handler(lh_conversation)

# Run the app
application.run_polling()
