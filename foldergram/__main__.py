import argparse
from . import bot

parser = argparse.ArgumentParser()
parser.add_argument('--bot', '-b')
parser.add_argument('--proxy', '-p')
parser.add_argument('--token', '-t')
args = parser.parse_args()

bot.start(args.bot, args.proxy, args.token)