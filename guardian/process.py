import re

COMMAND_REGEX = re.compile(
    r"(?P<trigger>cb |bc |!)(?P<command>[a-zA-Z]+)(?P<option> .+)*"
)


def hello(message, option):
    return message.channel.send(f"Hello <@{message.author.id}> !")


COMMANDS = {"hello": hello}


def process_message(message):
    matches = re.search(COMMAND_REGEX, message.content)
    if matches:
        command_name = matches.group("command")
        if COMMANDS.get(command_name):
            option = matches.group("option")
            return COMMANDS[command_name](message, option)
