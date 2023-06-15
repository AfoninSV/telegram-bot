from .commands import start, ask_category, low_reply, high_reply, cancel, button
from telegram.ext import (CommandHandler, ConversationHandler,
                          MessageHandler, CallbackQueryHandler,
                          filters)
from warnings import filterwarnings
from telegram.warnings import PTBUserWarning

#filterwarnings(action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning)

start_handler = CommandHandler('start', start)

lh_conversation = ConversationHandler(
    entry_points=[CommandHandler("low", ask_category),
                  CommandHandler("high", ask_category)],
    states={
        0: [MessageHandler(filters.TEXT, cancel)],
        # For /low, /high commands
        1: [MessageHandler(filters.TEXT, low_reply)],
        2: [MessageHandler(filters.TEXT, high_reply)],
        3: [CallbackQueryHandler(button)]
    },
    fallbacks=[CommandHandler("cancel", cancel)],
    per_user=True
)
