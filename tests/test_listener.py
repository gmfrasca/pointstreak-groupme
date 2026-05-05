import unittest
from unittest import mock
from flask import Flask
from psgroupme.interfaces.listener import GroupmeListener, DiscordListener


class TestGroupmeListener(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.mock_bot = mock.MagicMock()
        self.groupme_listener = GroupmeListener(self.mock_bot)

    def tearDown(self):
        pass

    def test_process_message_calls_bot(self):
        data = b'{"text": "hello", "system": false, "sender_type": "user"}'
        self.groupme_listener.process_message(data)
        self.mock_bot.handle_msg.assert_called_once_with('hello', mock.ANY)

    def test_process_message_ignores_system_message(self):
        data = b'{"text": "hello", "system": true}'
        self.groupme_listener.process_message(data)
        self.mock_bot.handle_msg.assert_not_called()

    def test_process_message_ignores_bot_sender(self):
        data = b'{"text": "hello", "system": false, "sender_type": "bot"}'
        self.groupme_listener.process_message(data)
        self.mock_bot.handle_msg.assert_not_called()

    def test_process_message_invalid_json(self):
        self.groupme_listener.process_message(b'not json')
        self.mock_bot.handle_msg.assert_not_called()

    def test_get(self):
        data = b'{"text": "hello", "system": false, "sender_type": "user"}'
        with self.app.test_request_context('/', data=data, content_type='application/octet-stream'):
            self.groupme_listener.get()
        self.mock_bot.handle_msg.assert_called_once_with('hello', mock.ANY)

    def test_post(self):
        data = b'{"text": "hello", "system": false, "sender_type": "user"}'
        with self.app.test_request_context('/', method='POST', data=data, content_type='application/octet-stream'):
            self.groupme_listener.post()
        self.mock_bot.handle_msg.assert_called_once_with('hello', mock.ANY)


class TestDiscordListener(unittest.TestCase):
    def setUp(self):
        self.mock_bot = mock.MagicMock()
        self.discord_listener = DiscordListener(self.mock_bot, '1234567890')

    def test_channel_id_set(self):
        self.assertEqual(self.discord_listener.channel_id, '1234567890')

    def test_process_message_calls_bot(self):
        mock_message = mock.MagicMock()
        mock_message.content = 'hello'
        mock_message.author.bot = False
        self.discord_listener.process_message(mock_message)
        self.mock_bot.handle_msg.assert_called_once_with('hello', metadata={'channel_id': mock_message.channel.id})

    def test_process_message_ignores_bot_author(self):
        mock_message = mock.MagicMock()
        mock_message.content = 'hello'
        mock_message.author.bot = True
        self.discord_listener.process_message(mock_message)
        self.mock_bot.handle_msg.assert_not_called()
