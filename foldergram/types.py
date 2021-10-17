import os
import mimetypes
from .utils import sort_like_explorer

import logging

logging.basicConfig(
    filename='log.txt',
    filemode='w',
    encoding='utf-8',
    format='%(filename)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)


COMMAND_DIR = 'commands'
TOKEN_FILE = 'token.txt'
ENCODING = 'utf-8'


class Attachment:
    types = ('image', 'audio', 'video')

    def __init__(self, file_path):
        self.file_path = file_path
        self.description = ''
        self.type = None

        self._parse()

        logging.debug(f"[class Attachment] {self.file_path=}")
        logging.debug(f"[class Attachment] {len(self.description)=}")
        logging.debug(f"[class Attachment] {self.type=}")

    def _parse(self):
        # get description
        desc_file = os.path.join(self.file_path, os.path.splitext(self.file_path)[0]) + '.txt'
        if os.path.isfile(desc_file) and desc_file != self.file_path:
            with open(desc_file, encoding=ENCODING) as f:
                self.description = f.read()

        # guess type file
        mime_type = mimetypes.guess_type(self.file_path)[0]
        if mime_type:
            if mime_type.split('/')[0] in self.types:
                self.type = mime_type.split('/')[0]


class Command:
    def __init__(self, command_path):
        self.name = os.path.split(command_path)[1]
        self.full_name = '/' + self.name
        self.command_path = command_path
        self.message = None
        self.attachments = []

        logging.debug(f"[class Command] {command_path=}")

        self._parse()

    def __eq__(self, other):
        if self.name == other or self.full_name == other:
            return True
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def _parse(self):
        folders, files = sort_like_explorer(self.command_path)

        # clean from description files (we will check it in Attachment)
        files_tmp = [os.path.splitext(item)[0] for item in files]
        for item in set(files_tmp):
            if files_tmp.count(item) > 1:
                if os.path.isfile(os.path.join(self.command_path, item + '.txt')):
                    files.remove(item + '.txt')
        del files_tmp

        # read message in folder of command
        if os.path.isfile(os.path.join(self.command_path, self.name + '.txt')):
            with open(os.path.join(self.command_path, self.name + '.txt'), encoding=ENCODING) as msg_file:
                self.message = msg_file.read()
            logging.debug(f"[class Command] length message: {len(self.message)}")
            files.remove(self.name + '.txt')

        for attach in files:
            logging.debug(f"[class Command] add attach: {attach}")
            self.attachments.append(Attachment(os.path.join(self.command_path, attach)))


class Bot:
    def __init__(self, root_path):
        self.root_path = os.path.abspath(root_path)
        self.token = None
        self.commands = []

        logging.debug(f"[class Bot] {self.root_path=}")

        self._parse()

        logging.debug(f"[class Bot] {self.commands=}")
        logging.debug(f"[class Bot] {self.token=}")

    def _get_token(self):
        token = None
        if os.path.isfile(os.path.join(self.root_path, TOKEN_FILE)):
            logging.debug(f"[class Bot._get_token] file exists")
            with open(os.path.join(self.root_path, TOKEN_FILE), encoding=ENCODING) as token_file:
                token = token_file.read().strip()
        return token

    def _parse(self):
        # get token if file exists
        self.token = self._get_token()

        # folders are contain "commands"
        folders, _ = sort_like_explorer(os.path.join(self.root_path, COMMAND_DIR))
        logging.debug(f"[class Bot] {folders=}")
        self.commands = [Command(os.path.join(self.root_path, COMMAND_DIR, folder)) for folder in folders]

    def get_command(self, name):
        if name in self.commands:
            return self.commands[self.commands.index(name)]

    def get_command_names(self):
        return [cmd.name for cmd in self.commands]