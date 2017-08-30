from flask import request
from flask_restful import Resource
from responder import Responder
from config_manager import ConfigManager
import json


class BaseBot(Resource):
    BOT_NAME = 'BaseBot'

    def __init__(self):
        cfg_mgr = ConfigManager()
        self.bot_id = cfg_mgr.get_bot_id(self.BOT_NAME)
        assert self.bot_id is not None
        self.responder = Responder(self.bot_id)

    def handle_msg(self, msg):
        system = msg.get('system', True)
        sender_type = msg.get('sender_type', 'user')
        if system and sender_type != 'bot':
            self.respond(msg)

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
            logger.warning('Could not decode message: {0}'.format(data_str))
            return None
        return None


class ScheduleBot(BaseBot):
    
    BOT_NAME = 'TestBot'
    

   
