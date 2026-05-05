import unittest
from unittest import mock
import psgroupme
from psgroupme.bots.base_bot import BaseBot
from psgroupme.bots.bot_responses import BotResponseManager
from tests.psgm_mocks import MOCK_CFG, EXAMPLE_RESP_YAML
from tests.psgm_mocks import BotResponseManagerMock


class TestBaseBot(unittest.TestCase):

    @mock.patch('psgroupme.bots.base_bot.BotResponseManager')
    def setUp(self, mock_brm):
        bot_id = 0
        mock_cfg = MOCK_CFG['bots'][bot_id]
        self.bot = BaseBot(mock_cfg)
        self.bot.brm = BotResponseManagerMock()

    def tearDown(self):
        pass

    #TODO: Use generic responder instead of GroupmeResponder
    @mock.patch.object(psgroupme.interfaces.responder.GroupmeResponder, 'reply')
    def test_respond(self, reply_fn):
        self.bot.respond("foobar")
        reply_fn.assert_called_once_with('foobar')

    def test_includes_standard_replies(self):
        self.bot.refresh_responses()
        brm = BotResponseManager(cfg_path=EXAMPLE_RESP_YAML)
        for resp_item in brm.get_global_responses():
            assert resp_item in self.bot.responses

    def test_excludes_specialized_replies(self):
        self.bot.refresh_responses()
        brm = BotResponseManager(cfg_path=EXAMPLE_RESP_YAML)
        for resp_item in brm.get_responses().get('base', list()):
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

    # TODO: These are now handled by the listener, move to different test
    # def test_ignore_system_msg(self):
    #     self.bot.read_msg = mock.MagicMock()
    #     test_msg = {
    #         'text': 'I am a system message',
    #         'system': True,
    #         'sender_type': 'user'
    #     }
    #     self.bot.handle_msg(test_msg)
    #     self.bot.read_msg.assert_not_called()

    # def test_ignore_bot_msg(self):
    #     self.bot.read_msg = mock.MagicMock()
    #     test_msg = {
    #         'text': 'I am a bot message',
    #         'system': False,
    #         'sender_type': 'bot'
    #     }
    #     self.bot.handle_msg(test_msg)
    #     self.bot.read_msg.assert_not_called()

    def test_read_msg(self):
        self.bot.respond = mock.MagicMock()
        self.bot.refresh_responses = mock.MagicMock()
        self.bot.get_params = mock.MagicMock()
        self.bot.responses = [
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
        self.bot.refresh_responses.assert_called_once()

        test_msg = dict(text='foobar')
        self.bot.read_msg(test_msg)
        self.bot.respond.assert_called_with(['helloworld'])
        self.bot.refresh_responses.assert_called()

        test_msg = dict(text='1test2')
        self.bot.read_msg(test_msg)
        self.bot.respond.assert_called_with(['testregex'])
        self.bot.refresh_responses.assert_called()

        # test_msg = dict(text='format_test')
        # self.bot.read_msg(test_msg)
        # self.bot.respond.assert_called_with([BOTNAMES[self.bot.bot_type]])
        # self.bot.refresh_responses.assert_called()