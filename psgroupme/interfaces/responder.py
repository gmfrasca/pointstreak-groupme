from requests import post
import logging
import random

GROUPME_BOT_URL = 'https://api.groupme.com/v3/bots/post'


class Responder(object):

    def __init__(self, bot_id, live=True):
        """Initialize this responder by assigning a bot"""
        self.bot_id = bot_id
        self.live = live

    def reply(self, message, context=None):
        """Post a message to the GroupMe REST API"""
        if not message or message == '':
            return
        if isinstance(message, list):
            message = random.choice(message)
        if context:
            message.format(**context)
        data = dict(bot_id=self.bot_id, text=message)
        if self.live:
            resp = post(GROUPME_BOT_URL, data=data)
            assert resp.status_code in range(200, 400)
        else:
            logging.info("Response: {}".format(message))
            print(message)
