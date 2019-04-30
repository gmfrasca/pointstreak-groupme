from requests.exceptions import ConnectionError
from requests import post
import logging

GROUPME_BOT_URL = 'https://api.groupme.com/v3/bots/post'


class Responder(object):

    def __init__(self, bot_id):
        """Initialize this responder by assigning a bot"""
        self._logger = logging.getLogger(self.__class__.__name__)
        self.bot_id = bot_id

    def reply(self, message):
        """Post a message to the GroupMe REST API"""
        if not message or message == '':
            return
        data = dict(bot_id=self.bot_id, text=message)
        try:
            self._logger.debug("Posting to {}: {}".format(GROUPME_BOT_URL,
                                                          data))
            resp = post(GROUPME_BOT_URL, data=data)
            assert resp.status_code in range(200, 400)
        except (AssertionError, ConnectionError):
            self._logger.exception("Could not post msg to Groupme Endpoint")
