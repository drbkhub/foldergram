from . import setting

def isAdmin(message):
    if message.from_user.id in setting.bot.admins:
        return True
    return False

def is_command(message):
    if setting.bot.get_command(message.get_command()):
        print(bool(setting.bot.get_command(message.get_command())))
        return True
    return False

def is_alias(message):
    if setting.bot.get_command_by_alias(message.text.lower().strip()):
        return True
    return False