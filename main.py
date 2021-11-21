from foldergram.bot import start
import sys, os

if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
    # print(f'{sys.executable=}')
elif __file__:
    application_path = os.path.dirname(__file__)

start(application_path)