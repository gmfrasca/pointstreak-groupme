from flask_restful import Resource
from flask import request
from psgroupme.interfaces.responder import GroupmeResponder
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


class LivePingBot(PingBot):

    def respond(self, msg):
        # TODO: Use factory to get the correct responder instead of GroupmeResponder
        GroupmeResponder(self.bot_id).reply("pong")

