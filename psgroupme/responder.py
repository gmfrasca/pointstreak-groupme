from requests import post

class Responder(object):

    GROUPME_BOT_URL = 'https://api.groupme.com/v3/bots/post'

    def __init__(self, bot_id):
        self.bot_id = bot_id

    def reply(self, message):
        data = dict(bod_id=self.bot_id, text=message)
        post(GROUPME_BOT_URL, json=data)
