from requests.exceptions import ConnectionError
from requests import post
import logging
import random
import json

GROUPME_BOT_URL = 'https://api.groupme.com/v3/bots/post'


class Responder(object):

    def __init__(self, bot_id):
        """Initialize this responder by assigning a bot"""
        self._logger = logging.getLogger(self.__class__.__name__)
        self.bot_id = bot_id

    def _send(self, url, data):
        return post(url, data=data)

    def reply(self, message):
        """Post a message to the GroupMe REST API"""
        if not message or message == '':
            return
        if isinstance(message, list):
            message = random.choice(message)
        data = dict(bot_id=self.bot_id, text=message)

        # NOTE(gfrasca): Sometime between 2020-12-31 and 2021-03-27 the
        # Groupme API appeared to stop taking direct JSON as a data input.
        # Sending this as a string seems to be a workaround, but there is no
        # documentation stating this change
        data = json.dumps(data)
        try:
            self._logger.debug("Posting to {}: {}".format(GROUPME_BOT_URL,
                                                          data))
            resp = self._send(GROUPME_BOT_URL, data)
            assert resp.status_code in range(200, 400)
        except (AssertionError, ConnectionError):
            self._logger.exception("Could not post msg to Groupme Endpoint")


class DebugResponder(Responder):
    class MockResponse(object):

        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

    def _send(self, url, data):
        self._logger.info("DEBUG Response: {}".format(data.get('text')))
        return self.MockResponse(data, 200)
