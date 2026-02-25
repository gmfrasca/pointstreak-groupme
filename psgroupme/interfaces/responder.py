from requests.exceptions import ConnectionError
from requests import post
import logging
import random
import json

GROUPME_BOT_URL = 'https://api.groupme.com/v3/bots/post'


class ResponderFactory(object):
    def __init__(self, *args, **kwargs):
        self._logger = logging.getLogger(self.__class__.__name__)

    def get_responder(self, responder_type, *args, **kwargs):
        if responder_type == 'groupme':
            return GroupmeResponder(*args, **kwargs)
        elif responder_type == 'debug':
            return DebugResponder(*args, **kwargs)
        else:
            # For now, default to GroupmeResponder for backwards compatibility
            self._logger.warning("Responder type '{0}' not found, using GroupmeResponder".format(responder_type))
            return GroupmeResponder(*args, **kwargs)

class Responder(object):

    host_type = None

    def __init__(self, *args, **kwargs):
        """Initialize this responder by assigning a bot"""
        self._logger = logging.getLogger(self.__class__.__name__)

    def _send(self, url, data):
        raise NotImplementedError("Subclasses must implement this method")

    def reply(self, message):
        raise NotImplementedError("Subclasses must implement this method")

class GroupmeResponder(Responder):

    host_type = 'flask'

    def __init__(self, bot_id, bot_url=None, *args, **kwargs):
        super(GroupmeResponder, self).__init__(bot_id, *args, **kwargs)
        self.bot_id = bot_id
        self.bot_url = bot_url

    def send(self, url, data):
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
            resp = self.send(GROUPME_BOT_URL, data)
            assert resp.status_code in range(200, 400)
        except (AssertionError, ConnectionError):
            self._logger.exception("Could not post msg to Groupme Endpoint")


class DebugResponder(GroupmeResponder):

    class MockResponse(object):

        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

    def send(self, url, data):
        data = json.loads(data)
        self._logger.info("DEBUG Response: {}".format(data.get('text')))
        return self.MockResponse(data, 200)
