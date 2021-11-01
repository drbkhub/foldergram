import os
import re
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

SETTING_DIR = 'setting'
COMMAND_DIR = 'commands'
ALIAS_DIR = 'aliases'
KEYBOARD_DIR = 'keyboards'
TOKEN_FILE = 'token.txt'
PROXY_FILE = 'proxy.txt'
ENCODING = 'utf-8'


class Attachment:
    types = ('image', 'audio', 'video', 'text')

    def __init__(self, file_path):
        self.file_path = file_path
        self.description = ''
        self.message = None
        self.type = None
        self.cache_id = None

        self._parse()

        logging.debug(f"[class Attachment] {self.file_path=}")
        logging.debug(f"[class Attachment] {len(self.description)=}")
        logging.debug(f"[class Attachment] {self.type=}")

    def __str__(self) -> str:
        return f'Attachment("{self.file_path}")'
    __repr__ = __str__

    @property
    def pretty_name(self):
        name = os.path.split(self.file_path)[1]
        prefix = re.findall(r"^\d+[\._ ]\s*", name)
        if prefix:
            return name[len(prefix[0]):]
        return name

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
    
    @classmethod
    def parse_attachments(cls, command_path):
        folders, files = sort_like_explorer(command_path)

        # clean from description files 
        files_tmp = [os.path.splitext(item)[0] for item in files]
        for item in set(files_tmp):
            if files_tmp.count(item) > 1:
                if os.path.isfile(os.path.join(command_path, item + '.txt')):
                    files.remove(item + '.txt')
        del files_tmp

        attachments = []
        for file in files:
            logging.debug(f"[class Command] add attach: {file}")
            attachments.append(Attachment(os.path.join(command_path, file)))
        return attachments


class Command:
    def __init__(self, command_path):
        self.name = os.path.split(command_path)[1]
        self.full_name = '/' + self.name
        self.command_path = command_path
        self.attachments = []
        self.aliases = []
        self.keyboard = None

        logging.debug(f"[class Command] {command_path=}")

        self._parse()

    def __eq__(self, other):
        if self.name == other or self.full_name == other:
            return True
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    @classmethod
    def parse_commands(cls, root_path):
        # folders are contain "commands"
        folders, _ = sort_like_explorer(os.path.join(root_path, COMMAND_DIR))
        logging.debug(f"[class Command] {folders=}")
        return [cls(os.path.join(root_path, COMMAND_DIR, folder)) for folder in folders]

    def _parse_aliases(self):
        alias_file = os.path.join(self.command_path, SETTING_DIR, 'alias.txt')
        if os.path.isfile(alias_file):
            with open(alias_file, encoding=ENCODING) as f:
                self.aliases.extend([line.lower() for line in f.read().splitlines() if line != ''])
                logging.debug(f"[class Command] found aliases: {len(self.aliases)}")
    
    def _parse_keyboard(self):
        keyboard_file = os.path.join(self.command_path, SETTING_DIR, 'keyboard.txt')
        if os.path.isfile(keyboard_file):
            with open(keyboard_file, encoding=ENCODING) as f:
                self.keyboard = [line for line in f.read().splitlines() if line != '']
                logging.debug(f"[class Command] found keyboard buttons: {len(self.keyboard)}")

    def _parse(self):
        # parse attachment 
        self.attachments = Attachment.parse_attachments(self.command_path)
        # parse alias file
        self._parse_aliases()
        # parse keyboars buttons
        self._parse_keyboard()

class Bot:
    def __init__(self, root_path, proxy=None, token=None):
        self.root_path = os.path.abspath(root_path)
        self.token = token
        self.proxy = proxy
        self.commands = []

        logging.debug(f"[class Bot] {self.root_path=}")

        self._parse()

        logging.debug(f"[class Bot] {self.commands=}")
        logging.debug(f"[class Bot] {self.token=}")
        logging.debug(f"[class Bot] {self.proxy=}")

    def _get_token(self):
        if os.path.isfile(os.path.join(self.root_path, TOKEN_FILE)) and self.token is None:
            logging.debug(f"[class Bot._get_token] file exists")
            with open(os.path.join(self.root_path, TOKEN_FILE), encoding=ENCODING) as token_file:
                self.token = token_file.read().strip()
        return self.token

    def _get_proxy(self):
        if os.path.isfile(os.path.join(self.root_path, PROXY_FILE)) and self.proxy is None:
            logging.debug(f"[class Bot._get_proxy] file exists")
            with open(os.path.join(self.root_path, PROXY_FILE), encoding=ENCODING) as proxy_file:
                self.proxy = proxy_file.read().strip()
        return self.proxy

    def _parse(self):
        # get token if file exists
        self.token = self._get_token()
        # get proxy if file exists
        self.proxy = self._get_proxy()
        # parse commdands
        self.commands = Command.parse_commands(self.root_path)

    def get_command(self, name):
        if name in self.commands:
            return self.commands[self.commands.index(name)]

    def get_command_names(self):
        return [cmd.name for cmd in self.commands]

    def get_aliases_names(self):
        alises = []
        for cmd in self.commands:
            alises.extend(cmd.aliases)
        return alises
    
    def get_command_by_alias(self, name):
        for cmd in self.commands:
            if name in cmd.aliases:
                return cmd
