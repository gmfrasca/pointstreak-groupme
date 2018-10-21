from flask import request
from flask_restful import Resource
from interfaces.responder import Responder
from bot_responses import BotResponseManager
import json
import re
import os


class BaseBot(Resource):
    """
    A basic GroupMe Bot. Responds to messages if they match the input regex
    found in bot_responses.py
    """

    @property
    def bot_type(self):
        return type(self).__name__

    def __init__(self, bot_cfg):
        """Load the config for this bot based on Name"""
        self.brm = BotResponseManager()
        self.bot_data = bot_cfg
        self.bot_id = self.bot_data.get('bot_id')
        self.bot_name = self.bot_data.get('bot_name', 'UnknownBot')
        assert self.bot_id is not None
        self.responder = Responder(self.bot_id)

    def refresh_responses(self):
        self.responses = self.brm.get_global_responses()
        self.responses.extend(self.get_bot_specific_responses())

    def get_bot_specific_responses(self):
        """Override this method to add bot-specific responses"""
        return []

    def handle_msg(self, msg):
        """Check if a message is actionable (not system or bot), and respond"""
        system = msg.get('system', True)
        sender_type = msg.get('sender_type', 'user')
        if not system and sender_type != 'bot':
            self.read_msg(msg)

    def get_matching_responses(self, msg):
        context = msg.copy()
        context.update(self.bot_data)
        return [x for x in self.responses if re.search(
                   x['input'].format(**context), msg['text'], re.I | re.U)]

    def get_extra_context(self):
        return self.brm.get_extra_context()

    def read_msg(self, msg):
        """
        Read a message's contents, and act on it if it matches a regex in
        self.responses.  Also updates the incoming message with the bot cfg for
        extra context (usefull in replies, such as {bot_name})
        """
        if msg['text'] == '!ping':
            self.respond('pong')
        self.refresh_responses()
        matches = self.get_matching_responses(msg)
        if len(matches) > 0:
            matches = self.get_matching_responses(msg)
            context = msg.copy()
            context.update(self.bot_data)
            context.update(self.get_extra_context())
            for match in matches:
                params = self.get_params(match, msg)
                try:
                    self.react(msg, context, params)
                    if 'reply' in matches[0]:
                        self.respond(matches[0]['reply'].format(**context))
                except KeyError:
                    # message requires undefined context variable
                    self.respond('Sorry, that command is not available.')

    def respond_image(self, searchfor):
        searchfor = os.path.basename(searchfor)
        public_url = self.bot_data.get('public_url').strip('/')
        img_cfg = self.bot_data.get('img_cfg')
        searchdir = img_cfg.get('path')
        dest = img_cfg.get('dest').strip('/')
        file_exts = ['.jpg', '.jpeg', '.gif', '.png', '.bmp']
        if img_cfg and searchdir and dest:
            # This is for ACL reasons
            found_files = [x for x in os.listdir(searchdir) if
                           os.path.isfile(os.path.join(searchdir, x))]
            for file_type in file_exts:
                filename = '{}{}'.format(searchfor, file_type)
                if filename in found_files:
                    url = '{}/{}/{}'.format(public_url, dest, filename)
                    self.respond(url)
                    return

    def react(self, msg, context, params):
        if msg.get('text', '').startswith("!img"):
            for param in params:
                self.respond_image(param)

    def respond(self, msg):
        """Have the bot post a message to it's group"""
        self.responder.reply(msg)

    def get(self):
        """React to a GET call"""
        return {'bot_cfg': self.bot_data}

    def post(self):
        """React to a POST call"""
        data_str = request.data
        try:
            msg = json.loads(data_str)
            self.handle_msg(msg)
            return {'post': msg}
        except ValueError:
            pass
        return None
