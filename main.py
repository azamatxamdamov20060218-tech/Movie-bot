#!/usr/bin/env python3
"""
Telegram Movie Bot
Main entry point for the bot application
"""

import logging
import os
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from bot.handlers import BotHandlers
from bot.config import Config

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    """Start the bot."""
    # Get bot token from environment variables
    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        logger.error("BOT_TOKEN environment variable is required")
        return

    # Create the Application
    application = Application.builder().token(bot_token).build()

    # Initialize bot handlers
    bot_handlers = BotHandlers()

    # Add handlers
    application.add_handler(CommandHandler("start", bot_handlers.start))
    application.add_handler(CommandHandler("admin", bot_handlers.admin_panel))
    application.add_handler(CommandHandler("add_movie", bot_handlers.add_movie))
    application.add_handler(CommandHandler("remove_movie", bot_handlers.remove_movie))
    application.add_handler(CommandHandler("list_movies", bot_handlers.list_movies))
    application.add_handler(CommandHandler("stats", bot_handlers.stats))
    application.add_handler(CommandHandler("language", bot_handlers.language_menu))

    # Callback query handler for inline keyboards
    application.add_handler(CallbackQueryHandler(bot_handlers.button_callback))

    # Message handler for movie codes and file uploads
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot_handlers.handle_message))
    application.add_handler(MessageHandler(filters.Document.ALL | filters.VIDEO, bot_handlers.handle_file))

    # Run the bot until the user presses Ctrl-C
    logger.info("Starting bot...")
    application.run_polling(allowed_updates=["message", "callback_query"])

if __name__ == '__main__':
    from keep_alive import keep_alive
    keep_alive()  # Doimiy ishlash uchun veb-serverni ishga tushuradi
    main()
    from keep_alive import keep_alive

    keep_alive()  # Web serverni ishga tushiradi (Replit uni uyg‘otib turadi)
from keep_alive import keep_alive

def main():
    application.run_polling()  # yoki sizdagi Application() holatiga qarab

if __name__ == "__main__":
    keep_alive()
    main()
    from keep_alive import keep_alive

    keep_alive()  # Web serverni ishga tushiradi (Replit uni uyg‘otib turadi)
    main()        # Botni ishga tushiradi