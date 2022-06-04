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
setting.bot = types.Bot(args.bot, proxy=args.proxy, token=args.token)

print('foldergram...')
bot.start()