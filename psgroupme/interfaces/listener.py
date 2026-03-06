from flask_restful import Resource
from flask import request
import json
import logging

class Listener(object):

    def __init__(self, bot, *args, **kwargs):
        self._logger = logging.getLogger(self.__class__.__name__)
        self.bot = bot

    def process_message(self, message):
        self.bot.handle_msg(message, metadata={})

class GroupmeListener(Listener, Resource):
    def __init__(self, bot, *args, **kwargs):
        
        Listener.__init__(self, bot, *args, **kwargs)
        Resource.__init__(self)

    def process_message(self, data):
        '''Process and forward a message to the bot'''
        try:
            msg = json.loads(data)
            msg_text = msg.pop('text')

            system = msg.get('system', True)
            sender_type = msg.get('sender_type', 'user')
            if not system and sender_type != 'bot':
                self.bot.handle_msg(msg_text, msg)
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

    def process_message(self, message):
        '''Process and forward a message to the bot'''
        text = message.content
        if not message.author.bot:
            self.bot.handle_msg(text, metadata={"channel_id": message.channel.id})
            self._logger.info("Message processed: {}".format(text))
