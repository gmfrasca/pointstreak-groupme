from flask_restful import Resource
from flask import request
import json
import logging

class Listener(object):

    def __init__(self, bot, *args, **kwargs):
        self._logger = logging.getLogger(self.__class__.__name__)
        self.bot = bot

    def process_message(self, message):
        self.bot.handle_msg(message)

class GroupmeListener(Listener, Resource):
    def __init__(self, bot, *args, **kwargs):
        
        Listener.__init__(self, bot, *args, **kwargs)
        Resource.__init__(self)

    def process_message(self, data):
        '''Process and forward a message to the bot'''
        try:
            msg = json.loads(data)
            self.bot.handle_msg(msg)
            return msg
        except ValueError:
            self._logger.error("Error parsing message: {}".format(data))

    def get(self):
        '''React to a GET call'''
        self._logger.info("Received GET call")
        return self.process_message(request.data)

    def post(self):
        '''React to a POST call'''
        self._logger.info("Received POST call")
        return self.process_message(request.data)

class DiscordListener(Listener):
    def __init__(self, bot, channel_id, *args, **kwargs):
        super(DiscordListener, self).__init__(bot, *args, **kwargs)
        self.channel_id = channel_id
