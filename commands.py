import os

COMMANDS_FILE = 'commands.txt'

def get_commands():
    if not os.path.exists(COMMANDS_FILE):
        return []
    
    with open(COMMANDS_FILE, 'r') as file:
        return [line.strip() for line in file.readlines()]

def add_command(command: str):
    with open(COMMANDS_FILE, 'a') as file:
        file.write(command + '\n')

def delete_command(command_index: int):
    commands = get_commands()
    
    if 0 <= command_index < len(commands):
        del commands[command_index]
        with open(COMMANDS_FILE, 'w') as file:
            file.write('\n'.join(commands) + '\n')
        return True
    return False
