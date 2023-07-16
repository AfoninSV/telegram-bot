from loader import bot, server
from telegram_bot import handlers

if __name__ == "__main__":

    # Run the app
    bot.infinity_polling()
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))

