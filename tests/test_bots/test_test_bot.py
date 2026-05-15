import unittest
from psgroupme.bots.test_bot import TestBot
from tests.psgm_mocks import BotResponseManagerMock
from unittest import mock

class TestTestBot(unittest.TestCase):
    CFG = {
        'bots': [
            {
                "class_name": "bots.TestBot", 
                "bot_name": "TestBot", 
                "bot_id": "0", 
                "bot_url": "/testbot", 
            }
        ]
    }

    @mock.patch('psgroupme.bots.base_bot.BotResponseManager', return_value=BotResponseManagerMock())
    def setUp(self, mock_brm):
        self.bot = TestBot(self.CFG['bots'][0])

    @mock.patch('psgroupme.bots.test_bot.DebugResponder')
    def test_test_bot(self, mock_debug_responder):
        self.bot.respond("test")
        self.assertIsInstance(self.bot.responder, mock.MagicMock)