import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--bot', '-b')
parser.add_argument('--proxy', '-p')
args = parser.parse_args()

print(args)