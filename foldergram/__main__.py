import argparse
from . import bot
from . import setting
from . import types

parser = argparse.ArgumentParser()
parser.add_argument('--bot', '-b')
parser.add_argument('--proxy', '-p')
parser.add_argument('--token', '-t')
args = parser.parse_args()

setting.args = args
print(f"Запускаю бота")
setting.bot = types.Bot(args.bot, proxy=args.proxy, token=args.token)
print(f"Количество комманд: {len(setting.bot.commands)}")

bot.start()