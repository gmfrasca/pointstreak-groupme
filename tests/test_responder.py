from psgroupme.interfaces.responder import Responder, GROUPME_BOT_URL
import unittest
import mock


def mocked_post(*args, **kwargs):
    class MockResponse(object):

        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code
    return MockResponse(args[0], 200)


class TestConfigManager(unittest.TestCase):

    def setUp(self):
        self.bot_id = '12345'
        self.responder = Responder(self.bot_id)

    def tearDown(self):
        pass

    @mock.patch('psgroupme.interfaces.responder.post', side_effect=mocked_post)
    def test_reply(self, mock_post):
        reply_text = 'foo'
        expected_data = dict(text=reply_text, bot_id=self.bot_id)
        self.responder.reply(reply_text)
        mock_post.assert_called_once_with(GROUPME_BOT_URL, data=expected_data)

    @mock.patch('psgroupme.interfaces.responder.post', side_effect=mocked_post)
    def test_blank_reply(self, mock_post):
        reply_text = ''
        self.responder.reply(reply_text)
        mock_post.assert_not_called()

        reply_text = None
        self.responder.reply(reply_text)
        mock_post.assert_not_called()
