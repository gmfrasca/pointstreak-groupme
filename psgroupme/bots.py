from flask import request
from flask_restful import Resource
from responder import Responder
from config_manager import ConfigManager
import bot_responses
import json
import re


class BaseBot(Resource):
    """
    A basic GroupMe Bot. Responds to messages if they match the input regex
    found in bot_responses.py
    """

    BOT_NAME = 'BaseBot'

    def __init__(self, cfg_path=None):
        """Load the config for this bot based on Name"""
        # Get the Bot Config
        self.cfg_mgr = ConfigManager(cfg_path)
        self.bot_data = self.cfg_mgr.get_bot_data(self.BOT_NAME)
        self.bot_id = self.cfg_mgr.get_bot_id(self.BOT_NAME)
        assert self.bot_id is not None

        # Set up the Responder
        self.responder = Responder(self.bot_id)
        self.responses = bot_responses.GLOBAL_RESPONSES

    def handle_msg(self, msg):
        """Check if a message is actionable (not system or bot), and respond"""
        system = msg.get('system', True)
        sender_type = msg.get('sender_type', 'user')
        if not system and sender_type != 'bot':
            self.read_msg(msg)

    def read_msg(self, msg):
        """
        Read a message's contents, and act on it if it matches a regex in
        self.responses.  Also updates the incoming message with the bot cfg for
        extra context (usefull in replies, such as {bot_name})
        """
        context = msg.copy()
        context.update(self.bot_data)
        matches = [x for x in self.responses if re.search(
           x['input'].format(**context), msg['text'], re.I | re.U)]
        if len(matches) > 0:
            self.respond(matches[0]['reply'].format(**context))

    def respond(self, msg):
        """Have the bot post a message to it's group"""
        self.responder.reply('Hello, this is {0}'.format(self.BOT_NAME))

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


class ScheduleBot(BaseBot):

    BOT_NAME = 'TestBot'

    def __init__(self):
        """Initialize the bot, and add ScheduleBot-specific responses"""
        super(ScheduleBot, self).__init__()
        self.responses.extend(bot_responses.SCHEDULE_BOT_RESPONSES)

    def respond(self, msg):
        """Respond using the matched message reply"""
        self.responder.reply(msg)
