from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InputTextMessageContent, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackContext, CallbackQueryHandler, ConversationHandler
from time import gmtime, strftime
from authentication import isAdminUser, add_admin_to_file
from servers import get_servers_data, is_valid_ip, del_server, is_valid_login, add_server, client, do_command, is_connected_to_server

# Helper function to get user info from update
def get_user_info(update: Update):
    if update.message:
        return update.message.chat.id, update.message.chat.username
    elif update.callback_query:
        return update.callback_query.message.chat.id, update.callback_query.from_user.username
    return None, None

# Start command with inline buttons
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Create inline keyboard with buttons for each command
    keyboard = [
        [InlineKeyboardButton("Add Server", callback_data="add_server")],
        [InlineKeyboardButton("Delete Server", callback_data="del_server")],
        [InlineKeyboardButton("List Servers", callback_data="list_servers")],
        [InlineKeyboardButton("Connect to Server", callback_data="connect_server")],
        [InlineKeyboardButton("Disconnect from Server", callback_data="disconnect_server")],
        [InlineKeyboardButton("Default Commands", callback_data="default_commands")],
        [InlineKeyboardButton("Help", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send message with inline keyboard
    await update.message.reply_text(
        'Welcome to **SSH Terminal Bot**\nChoose an action:',
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # Acknowledge the callback query

    # Handle different callback data values
    if query.data == "add_server":
        await query.message.reply_text("To add a server, use the command: /add_server [IP] [Username] [Password]")
    elif query.data == "del_server":
        await query.message.reply_text("To delete a server, use the command: /del_server [Server Number]")
    elif query.data == "list_servers":
        await servers_list(update, context)
    elif query.data == "connect_server":
        await query.message.reply_text("To connect to a server, use the command: /connect [Server Number]")
    elif query.data == "disconnect_server":
        await discconnect_from_server(update, context)
    elif query.data == "help":
        await help_command(update, context)
    elif query.data == "add_command":
        await query.message.reply_text("To add a command, use the command: /add_command [Your Command]")
    elif query.data == "remove_command":
        await query.message.reply_text("To remove a command, use the command: /remove_command [Command Number]")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text='Please check the repository for command guides: \n https://github.com/ItsOrv/SSH-TelegramBot')

async def add_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_chat_id, username = get_user_info(update)
    if isAdminUser(user_chat_id):
        data: str = update.message.text
        proccessed_data: str = data.replace("/add_admin", '').strip()
        print(f">> new admin added by ({username} {user_chat_id}). \n{proccessed_data} is now admin,\n")
        add_admin_to_file(proccessed_data)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"New admin added \n{proccessed_data} is now admin.")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="You dont have access to add a new admin.")

async def del_server_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_chat_id, username = get_user_info(update)

    if isAdminUser(user_chat_id) or isAdminUser(username):
        data: str = update.message.text
        proccessed_data: int = int(str(data.replace("/del_server", '').strip()))
        servers = get_servers_data()
        if int(proccessed_data) <= len(servers):
            del_server(int(proccessed_data))
            print(int(proccessed_data), len(servers))
            print(f'>> A server deleted by ({username} {user_chat_id})\n - Server IP : {servers[proccessed_data-1][0]}\n - Connection Info : {servers[proccessed_data-1][1]}:{servers[proccessed_data-1][2]}',
                end="")
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f'Server Deleted\n'
                                                f'Server IP : {servers[proccessed_data - 1][0]}\n'
                                                f'Connection Info : {servers[proccessed_data - 1][1]}:{servers[proccessed_data - 1][2]}\n'
                                                f'Deleted by : {user_chat_id} in {strftime("%Y-%m-%d %H:%M:%S", gmtime())}\n')
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f'Server doesnt exist, try again')
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f'You need admin access to delete to a server!')

async def add_server_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_chat_id, username = get_user_info(update)
    if isAdminUser(user_chat_id) or isAdminUser(username):
        data: str = update.message.text
        proccessed_data: str = data.replace("/add_server", '').strip()
        proccessed_data_list = proccessed_data.split()
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f'Checking validity of given ip')
        if is_valid_ip(proccessed_data_list[0]):
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f'IP validation successful.')
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f'Checking validity of login information')
            if is_valid_login(proccessed_data_list[0] , proccessed_data_list[1] , proccessed_data_list[2]):
                await context.bot.send_message(chat_id=update.effective_chat.id, text=f'Login information validation successful.')
                add_server(proccessed_data_list[0] , proccessed_data_list[1] , proccessed_data_list[2] , user_chat_id , strftime("%Y-%m-%d %H:%M:%S", gmtime()))
                print(f">> Adding a new server by : ({username} {user_chat_id}).\n"
                      f"    servers_list- Server Info: {proccessed_data}")
                await context.bot.send_message(chat_id=update.effective_chat.id, text=f'New server added! (status : Unknown)\n'
                                                f'Server IP : {proccessed_data_list[0]}\n'
                                                f'Connection Info : {proccessed_data_list[1]}:{proccessed_data_list[2]}\n'
                                                f'added by : {user_chat_id} in {strftime("%Y-%m-%d %H:%M:%S", gmtime())}\n')
            else:
                await context.bot.send_message(chat_id=update.effective_chat.id, text=f'Adding new server failed!\nEither username or password is not correct\nPlease try again.')
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f'Adding new server failed!\nPlease enter a valid IP.')
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f'You need admin access to add a new server!')

ADD_COMMAND = range(1)

async def add_command_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.reply_text("Please send the command you want to add:")
    return ADD_COMMAND

async def add_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    command = update.message.text.strip()
    with open('commands.txt', 'a') as file:
        file.write(f"{command}\n")
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Command {command} added successfully.", parse_mode="Markdown")
    return ConversationHandler.END

REMOVE_COMMAND = range(1)

async def remove_command_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    commands = get_default_commands()
    if not commands:
        await update.callback_query.message.reply_text("No commands to remove.")
        return ConversationHandler.END

    message = "Please send the number of the command you want to remove:\n"
    for idx, command in enumerate(commands, start=1):
        message += f"{idx}- {command}\n"
    await update.callback_query.message.reply_text(message)
    return REMOVE_COMMAND

async def remove_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    command_number = int(update.message.text.strip()) - 1
    commands = get_default_commands()

    if 0 <= command_number < len(commands):
        removed_command = commands.pop(command_number)
        with open('commands.txt', 'w') as file:
            for command in commands:
                file.write(f"{command}\n")
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Command {removed_command} removed successfully.", parse_mode="Markdown")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Invalid command number.")

    return ConversationHandler.END

def get_default_commands():
    commands = []
    try:
        with open('commands.txt', 'r') as file:
            commands = file.readlines()
    except FileNotFoundError:
        pass
    return [command.strip() for command in commands]

async def show_default_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    commands = get_default_commands()
    if commands:
        message = "Default Commands:\n\n"
        for idx, command in enumerate(commands, start=1):
            message += f"{idx}- {command}\n"
    else:
        message = "No commands found."

    # Add options to add or remove commands
    keyboard = [
        [InlineKeyboardButton("Add Command", callback_data="add_command")],
        [InlineKeyboardButton("Remove Command", callback_data="remove_command")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.message.reply_text(message, reply_markup=reply_markup, parse_mode="Markdown")

async def servers_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_chat_id, username = get_user_info(update)
    if isAdminUser(user_chat_id) or isAdminUser(username):
        print(f">> List of servers asked by : ({username} {user_chat_id}).")
        servers = get_servers_data()
        table = "All Servers:\n\n\n"
        counter = 1
        for server in servers:
            table += (f"Server Number : {counter}\n"
                      f"Server IP : {server[0]}\n"
                      f"Added By : {server[3]}\n"
                      f"Date Added : {server[4]}\n\n---------\n")
            counter += 1
        await context.bot.send_message(chat_id=update.effective_chat.id, text=table)
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f'You need admin access to view list of servers!')

async def connect_to_server_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_chat_id, username = get_user_info(update)
    global is_connected_to_server
    if isAdminUser(user_chat_id) or isAdminUser(username):
        if is_connected_to_server is False:
            data: str = update.message.text
            proccessed_data: str = data.replace("/connect", '').strip()

            # Validate if the user entered a number
            if not proccessed_data.isdigit():
                await context.bot.send_message(chat_id=update.effective_chat.id, text="Please provide a valid server number.")
                return

            proccessed_data = int(proccessed_data) - 1
            servers = get_servers_data()

            if proccessed_data >= len(servers) or proccessed_data < 0:
                await context.bot.send_message(chat_id=update.effective_chat.id, text="Invalid server number. Please try again.")
                return

            print(f'>> Trying to connect to server by ({username} {user_chat_id})\n - Server IP : {servers[proccessed_data][0]}\n - Connection Info : {servers[proccessed_data][1]}:{servers[proccessed_data][2]}\n - Result : ',
                  end="")
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f'Trying to connect to server\n'
                                            f'Server IP : {servers[proccessed_data][0]}\n'
                                            f'Connection Info : {servers[proccessed_data][1]}:{servers[proccessed_data][2]}\n'
                                            f'added by : {servers[proccessed_data][3]} in {servers[proccessed_data][4]}\n')
            try:
                client.connect(servers[proccessed_data][0], username=servers[proccessed_data][1],
                               password=servers[proccessed_data][2])
                print("Successfull!!\n")
                is_connected_to_server = True
                await context.bot.send_message(chat_id=update.effective_chat.id, text=f'Successfully connected to server!')
            except:
                print("Failed!\n")
                is_connected_to_server = False
                await context.bot.send_message(chat_id=update.effective_chat.id, text=f'Couldn\'t connect to server!')
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f'Already connected to server\nplease disconnect first using:\n/disconnect command')
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f'You need admin access to connect to a server!')

async def discconnect_from_server(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global is_connected_to_server
    user_chat_id, username = get_user_info(update)

    if isAdminUser(user_chat_id) or isAdminUser(username):
        print(
            f'>> Trying to close the connection by ({username} {user_chat_id})\n - Result : ',
            end="")
        if is_connected_to_server is True:
            client.close()
            is_connected_to_server = False
            print("Successfully closed the connection\n")
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Connection closed!")
        else:
            print("Failed - no connection found!\n")
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Failed to do the task! (you sure I was connected to a server?)")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f'You need admin access to disconnect from a server!')

def handle_command(text: str) -> str:
    proccessed_text = text.lower()
    global is_connected_to_server
    if is_connected_to_server is True:
        result = do_command(client, proccessed_text)
        return f"*Done!*\n
shell\n{proccessed_text}\n
\n*output:*\n
\n{result}
"
    else:
        return f"Im not connected to any server.\nPlease connect me with /connect command"

async def command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    print(f'>> user ({update.message.chat.first_name} {update.message.chat.last_name}) in {message_type}: "{text}"')

    if message_type == 'group' or message_type == 'supergroup':
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f'Currently Im not able to execute commands given in groups!')
        return
    else:
        response: str = handle_command(text)

    await context.bot.send_message(chat_id=update.effective_chat.id, text=response, parse_mode="markdown")

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused {context.error}')

import csv

COMMANDS_FILE = 'commands.txt'

async def add_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    command_text = update.message.text.replace("/add_command", "").strip()

    if command_text:
        with open(COMMANDS_FILE, "a") as file:
            file.write(f"{command_text}\n")
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Command added: {command_text}", parse_mode="Markdown")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Please provide a command to add using: /add_command [Your Command]")

async def remove_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        command_index = int(update.message.text.replace("/remove_command", "").strip()) - 1
    except ValueError:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Please provide a valid command number.")
        return

    commands = []
    with open(COMMANDS_FILE, "r") as file:
        commands = file.readlines()

    if 0 <= command_index < len(commands):
        removed_command = commands.pop(command_index)
        with open(COMMANDS_FILE, "w") as file:
            file.writelines(commands)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Command removed: {removed_command.strip()}", parse_mode="Markdown")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Invalid command number.")
