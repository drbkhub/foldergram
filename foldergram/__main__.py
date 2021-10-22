import argparse
from . import bot

parser = argparse.ArgumentParser()
parser.add_argument('--bot', '-b')
parser.add_argument('--proxy', '-p')
args = parser.parse_args()

print(args)

bot.start(args.bot, args.proxy)