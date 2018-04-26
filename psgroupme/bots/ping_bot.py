from flask_restful import Resource
from interfaces.responder import Responder


class PingBot(Resource):
    """
    A basic GroupMe Bot. Responds to messages if they match the input regex
    found in bot_responses.py
    """

    @property
    def bot_type(self):
        return type(self).__name__

    def __init__(self, bot_id, **kwargs):
        self.bot_id = bot_id

    def respond(self, msg):
        """Have the bot post a message to it's group"""
        print("pong")

    def get(self):
        """React to a GET call"""
        return {'bot_cfg': self.bot_data}

    def post(self):
        """React to a POST call"""
        try:
            self.respond("ping")
        except ValueError:
            pass
        return None


class LivePingBot(PingBot):

    def respond(self, msg):
        Responder(self.bot_id).reply("pong")
