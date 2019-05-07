from flask_restful import Resource
from flask import request
from psgroupme.interfaces.responder import Responder
import logging
import json


class PingBot(Resource):
    """
    A basic GroupMe Bot. Responds to messages if they match the input regex
    found in bot_responses.py
    """

    @property
    def bot_type(self):
        return type(self).__name__

    def __init__(self, bot_id, **kwargs):
        self._logger = logging.getLogger(self.__class__.__name__)
        self.bot_id = bot_id

    def respond(self, msg):
        """Have the bot post a message to it's group"""
        self._logger.info("pong")

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

    def post(self):
        data_str = request.data
        try:
            msg = json.loads(data_str)
            system = msg.get('system', True)
            sender_type = msg.get('sender_type', 'user')
            if not system and sender_type != 'bot':
                self._logger.info("User message recieved, responding")
                self.respond(msg)
            return {'post': msg}
        except ValueError:
            pass
        return None
