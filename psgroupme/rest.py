from flask import Flask, request
from flask_restful import Resource, Api
from responder import Responder
from config_manager import ConfigManager
import json

app = Flask(__name__)
api = Api(app)


class ScheduleBot(Resource):
    
    BOT_NAME = 'TestBot'

    def __init__(self):
        cfg_mgr = ConfigManager()
        self.bot_id = cfg_mgr.get_bot_id(self.BOT_NAME)
        assert self.bot_id is not None
        self.responder = Responder(self.bot_id)

    def handle_msg(self, msg):
        system = msg.get('system', True)
        sender_type = msg.get('sender_type', 'user')
        if system or sender_type == 'bot':
            return
        self.responder.reply('FOOBAR')
        return

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

api.add_resource(ScheduleBot, '/schedulebot')

if __name__ == '__main__':
    app.run(port='5002')


