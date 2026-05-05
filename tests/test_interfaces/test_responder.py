from psgroupme.interfaces.responder import ResponderFactory, GROUPME_BOT_URL
from psgroupme.interfaces.responder import GroupmeResponder, DebugResponder, DiscordResponder
import unittest
from unittest import mock
import json


def mocked_post(*args, **kwargs):
    class MockResponse(object):

        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code
    return MockResponse(args[0], 200)


class TestResponderFactory(unittest.TestCase):

    def setUp(self):
        self.factory = ResponderFactory()
        self.factory._logger = mock.MagicMock()

    def tearDown(self):
        pass

    @mock.patch('psgroupme.interfaces.clients.DiscordClientManager')
    def test_get_responder(self, mock_discord_client_manager):
        responders = [
            {'type': 'groupme', 'bot_id': '12345', 'expected_type': GroupmeResponder},
            {'type': 'debug', 'bot_id': '12345', 'expected_type': DebugResponder},
            {'type': 'discord', 'channel_id': '12345', 'expected_type': DiscordResponder},
            {'type': 'unknown', 'expected_type': None},
        ]
        for responder in responders:
            responder_instance = self.factory.get_responder(responder['type'], **responder)
            if responder['expected_type'] is None:
                self.assertIsNone(responder_instance)
            else:
                self.assertIsInstance(responder_instance, responder['expected_type']) 

    @mock.patch('psgroupme.interfaces.clients.DiscordClientManager', return_value=mock.MagicMock(discord_client=None))
    def test_discord_client_not_available(self, mock_discord_client_manager):
        mock_discord_client_manager.discord_client = None
        responder_instance = self.factory.get_responder('discord', channel_id='12345')
        self.assertIsNone(responder_instance)
        self.factory._logger.error.assert_called_once_with("Discord client is not available, cannot set up Discord responder")

class TestResponder(unittest.TestCase):

    def setUp(self):
        self.bot_id = '12345'
        self.responder_type = 'groupme'
        self.responder = ResponderFactory().get_responder(self.responder_type, self.bot_id)

    def tearDown(self):
        pass

    @mock.patch('psgroupme.interfaces.responder.post', side_effect=mocked_post)
    def test_reply(self, mock_post):
        reply_text = 'foo'
        expected_data = json.dumps(dict(bot_id=self.bot_id, text=reply_text))
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

    

    @mock.patch('psgroupme.interfaces.responder.random.choice', return_value='foo')
    def test_sanitize_message(self, mock_random_choice):
        reply_text = 'foo'
        self.assertEqual(self.responder._sanitize_message(reply_text), reply_text)

        reply_text = ''
        self.assertIsNone(self.responder._sanitize_message(reply_text))

        reply_text = None
        self.assertIsNone(self.responder._sanitize_message(reply_text))

        reply_text = ['foo', 'bar']
        self.assertEqual(self.responder._sanitize_message(reply_text), 'foo')
        mock_random_choice.assert_called_once_with(reply_text)


class TestGroupmeResponder(unittest.TestCase):
    def setUp(self):
        self.bot_id = '12345'
        self.responder = GroupmeResponder(self.bot_id)
        self.responder._logger = mock.MagicMock()
    def tearDown(self):
        pass

    @mock.patch('psgroupme.interfaces.responder.post', side_effect=mocked_post)
    def test_reply(self, mock_post):
        reply_text = 'foo'
        expected_data = json.dumps(dict(bot_id=self.bot_id, text=reply_text))
        self.responder.reply(reply_text)
        mock_post.assert_called_once_with(GROUPME_BOT_URL, data=expected_data)


class TestDiscordResponder(unittest.TestCase):
    def setUp(self):
        self.channel_id = '12345'
        mock_discord_client = mock.MagicMock()
        self.responder = DiscordResponder(self.channel_id, mock_discord_client)

    def tearDown(self):
        pass

    def test_reply(self):  
        reply_text = 'foo'  
        self.responder.reply(reply_text)
        self.responder.discord_client.send.assert_called_once_with(self.channel_id, reply_text)


class TestDebugResponder(unittest.TestCase):
    def setUp(self):
        self.bot_id = '12345'
        self.responder = DebugResponder(self.bot_id)
        self.responder._logger = mock.MagicMock()

    def tearDown(self):
        pass

    @mock.patch('psgroupme.interfaces.responder.DebugResponder._send', side_effect=mocked_post)
    def test_reply(self, mock_post):
        reply_text = 'foo'
        expected_data = json.dumps(dict(bot_id=self.bot_id, text=reply_text))
        self.responder.reply(reply_text)
        mock_post.assert_called_once_with(GROUPME_BOT_URL, expected_data)

    @mock.patch('psgroupme.interfaces.responder.DebugResponder._send', side_effect=mocked_post) # NOTE(gfrasca): This is a bit of a hack to get the test to pass
    def test_blank_reply(self, mock_post):
        reply_text = ''
        self.responder.reply(reply_text)
        mock_post.assert_not_called()

        reply_text = None
        self.responder.reply(reply_text)
        mock_post.assert_not_called()

    def test_send_to_logger(self):
        reply_text = 'foo'
        expected_reply_text = "DEBUG Response: {}".format(reply_text)
        self.responder.reply(reply_text)
        self.responder._logger.info.assert_called_once_with(expected_reply_text)