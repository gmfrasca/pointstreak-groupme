from flask import request
from flask_restful import Resource
from responder import Responder
from config_manager import ConfigManager
import bot_responses
import json
import re


class BaseBot(Resource):
    BOT_NAME = 'BaseBot'

    def __init__(self):
        self.cfg_mgr = ConfigManager()
        self.bot_data = self.cfg_mgr.get_bot_data(self.BOT_NAME)
        self.bot_id = self.cfg_mgr.get_bot_id(self.BOT_NAME)
        assert self.bot_id is not None
        self.responder = Responder(self.bot_id)
        self.responses = bot_responses.GLOBAL_RESPONSES

    def handle_msg(self, msg):
        system = msg.get('system', True)
        sender_type = msg.get('sender_type', 'user')
        if not system and sender_type != 'bot':
            self.read_msg(msg)

    def read_msg(self, msg):
        context = msg.copy()
        context.update(self.bot_data)
        matches = [x for x in self.responses if re.search(
           x['input'].format(**context), msg['text'], re.I | re.U)]
        if len(matches) > 0:
            self.respond(matches[0]['reply'].format(**context))

    def respond(self, msg):
        self.responder.reply('Hello, this is {0}'.format(self.BOT_NAME))

    def get(self):
        return {'foo': 'bar'}

    def post(self):
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
        super(ScheduleBot, self).__init__()
        self.responses.extend(bot_responses.SCHEDULE_BOT_RESPONSES)

    def respond(self, msg):
        self.responder.reply(msg)
