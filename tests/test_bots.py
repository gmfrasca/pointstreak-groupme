import psgroupme
from psgroupme.bots import BaseBot, ScheduleBot
from psgroupme.bot_responses import GLOBAL_RESPONSES, SCHEDULE_BOT_RESPONSES
import unittest
import mock
import json


MOCK_CFG = {
            'bots': [
                {
                     'bot_name': 'BaseBot',
                     'bot_id': '1',
                     'group_name': 'foo',
                     'group_id': '12345',
                     'callback_url': 'http://foo.bar',
                     'avatar_url': 'http://funny.jpg'
                 },
                {
                     'bot_name': 'TestBot',
                     'bot_id': '2',
                     'group_name': 'foo',
                     'group_id': '12345',
                     'callback_url': 'http://foo.bar',
                     'avatar_url': 'http://funny.jpg'
                 }
            ]
        }


class TestBaseBot(unittest.TestCase):

    @mock.patch.object(psgroupme.config_manager.ConfigManager, 'load_cfg')
    def setUp(self, mock_cfg_mgr_load):
        mock_cfg_mgr_load.return_value = MOCK_CFG
        self.bot = BaseBot()

    def tearDown(self):
        pass

    def test_get_request(self):
        expected = dict(bot_cfg=self.bot.bot_data)
        self.assertEqual(self.bot.get(), expected)

    @mock.patch("psgroupme.bots.request")
    def test_post_request(self, mocked_data):
        mocked_data.data = '{"foo": "bar"}'
        loaded_dict = json.loads(mocked_data.data)
        expected = dict(post=loaded_dict)
        self.bot.handle_msg = mock.MagicMock()
        self.assertEqual(self.bot.post(), expected)
        self.bot.handle_msg.assert_called_once_with(loaded_dict)

    @mock.patch("psgroupme.bots.request")
    def test_bad_post_request(self, mocked_data):
        mocked_data.data = '{"this_is_bad_json'
        self.bot.handle_msg = mock.MagicMock()
        self.assertEqual(self.bot.post(), None)
        self.bot.handle_msg.assert_not_called()

    @mock.patch.object(psgroupme.responder.Responder, 'reply')
    def test_respond(self, reply_fn):
        self.bot.respond("foobar")
        reply_fn.assert_called_once_with('Hello, this is {0}'.format(self.bot.BOT_NAME))


    def test_includes_standard_replies(self):
        for resp_item in GLOBAL_RESPONSES:
            assert resp_item in self.bot.responses

    def test_excludes_specialized_replies(self):
        for resp_item in SCHEDULE_BOT_RESPONSES:
            assert resp_item not in self.bot.responses

    def test_handle_msg(self):
        self.bot.read_msg = mock.MagicMock()
        test_msg = {
            'text': 'I am a user message',
            'system': False,
            'sender_type': 'user'
        }
        self.bot.handle_msg(test_msg)
        self.bot.read_msg.assert_called_once()

    def test_ignore_system_msg(self):
        self.bot.read_msg = mock.MagicMock()
        test_msg = {
            'text': 'I am a system message',
            'system': True,
            'sender_type': 'user'
        }
        self.bot.handle_msg(test_msg)
        self.bot.read_msg.assert_not_called()

    def test_ignore_bot_msg(self):
        self.bot.read_msg = mock.MagicMock()
        test_msg = {
            'text': 'I am a bot message',
            'system': False,
            'sender_type': 'bot'
        }
        self.bot.handle_msg(test_msg)
        self.bot.read_msg.assert_not_called()


    def test_read_msg(self):
        self.bot.respond = mock.MagicMock()
        self.bot.responses= [
            {
                'input': r'foobar',
                'reply': 'helloworld'
            },
            {
                'input': r'[0-9]test[0-9]',
                'reply': 'testregex'
            },
            {
                'input': r'format_test',
                'reply': '{bot_name}'
            }
        ]

        test_msg = dict(text='ignore_me')
        self.bot.read_msg(test_msg)
        self.bot.respond.assert_not_called()

        test_msg = dict(text='foobar')
        self.bot.read_msg(test_msg)
        self.bot.respond.assert_called_with('helloworld')

        test_msg = dict(text='1test2')
        self.bot.read_msg(test_msg)
        self.bot.respond.assert_called_with('testregex')

        test_msg = dict(text='format_test')
        self.bot.read_msg(test_msg)
        self.bot.respond.assert_called_with('{}'.format(self.bot.BOT_NAME))


class TestScheduleBot(TestBaseBot):

    @mock.patch.object(psgroupme.config_manager.ConfigManager, 'load_cfg')
    def setUp(self, mock_cfg_mgr_load):
        mock_cfg_mgr_load.return_value = MOCK_CFG
        self.bot = ScheduleBot()

    def test_includes_specialized_replies(self):
        for resp_item in SCHEDULE_BOT_RESPONSES:
            assert resp_item in self.bot.responses

    @mock.patch.object(psgroupme.responder.Responder, 'reply')
    def test_respond(self, reply_fn):
        test_msg = 'foobar'
        self.bot.respond(test_msg)
        reply_fn.assert_called_once_with(test_msg)

    def test_excludes_specialized_replies(self):
        pass
