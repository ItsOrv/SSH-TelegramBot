import os
from typing import Final
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackContext, CallbackQueryHandler
from bot import start_command, help_command, add_admin, add_server_handler, del_server_handler, servers_list, connect_to_server_handler, discconnect_from_server, command_handler, callback_handler, add_command, remove_command

TOKEN: Final = ''
BOT_USERNAME: Final = ""

# add .env
"""
TOKEN: str = os.getenv('TELEGRAM_BOT_TOKEN')
BOT_USERNAME: str = os.getenv('BOT_USERNAME', '@orvsshbot')
"""

if __name__ == '__main__':
    print("Starting bot...")
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('add_admin', add_admin))
    app.add_handler(CommandHandler('add_server', add_server_handler))
    app.add_handler(CommandHandler('del_server', del_server_handler))
    app.add_handler(CommandHandler('servers_list', servers_list))
    app.add_handler(CommandHandler('connect', connect_to_server_handler))
    app.add_handler(CommandHandler('disconnect', discconnect_from_server))
    
    # Add and Remove Commands
    app.add_handler(CommandHandler('add_command', add_command))
    app.add_handler(CommandHandler('remove_command', remove_command))

    # Handle button presses
    app.add_handler(CallbackQueryHandler(callback_handler))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT, command_handler))

    print("Bot is running...")
    app.run_polling(poll_interval=3)
