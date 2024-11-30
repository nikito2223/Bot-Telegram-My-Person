from telegram.ext import Application, CommandHandler, MessageHandler, ConversationHandler, filters
from db_manager import DatabaseManager
import settings
import character_manager
import logging
import os

# Define states for conversation
db = DatabaseManager()

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    DatabaseManager.create_table()  # Ensure the database and table exist

    # Replace with your Telegram Bot Token
    application = Application.builder().token(settings.BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", character_manager.start))
    application.add_handler(CommandHandler("list", DatabaseManager.list_characters))
    application.add_handler(CommandHandler("show", DatabaseManager.show_character))
    application.add_handler(CommandHandler("delete", DatabaseManager.delete_character))

    # Add conversation handler for character creation
    create_handler = ConversationHandler(
        entry_points=[CommandHandler("create", character_manager.create)],
        states={
            character_manager.AVATAR: [MessageHandler(filters.PHOTO, character_manager.avatar)],
            character_manager.NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, character_manager.name)],
            character_manager.DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, character_manager.description)],
            character_manager.HEALTH: [MessageHandler(filters.TEXT & ~filters.COMMAND, character_manager.health)],
            character_manager.DAMAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, character_manager.damage)],
            character_manager.ABILITIES: [MessageHandler(filters.TEXT & ~filters.COMMAND, character_manager.abilities)],
            character_manager.SKILLS: [MessageHandler(filters.TEXT & ~filters.COMMAND, character_manager.skills)],
        },
        fallbacks=[CommandHandler('cancel', character_manager.cancel)]
    )
    application.add_handler(create_handler)
    
    try:
        application.run_polling()
    except KeyboardInterrupt:
        logger.info("Bot has been stopped by user.")
    except Exception as e:
        logger.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()