from requests import post

GROUPME_BOT_URL = 'https://api.groupme.com/v3/bots/post'


class Responder(object):

    def __init__(self, bot_id):
        """Initialize this responder by assigning a bot"""
        self.bot_id = bot_id

    def reply(self, message):
        """Post a message to the GroupMe REST API"""
        data = dict(bot_id=self.bot_id, text=message)
        resp = post(GROUPME_BOT_URL, data=data)
        assert resp.status_code in range(200, 399)
