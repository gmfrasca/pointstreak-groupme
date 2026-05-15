import unittest
from psgroupme.bots.master_bot import MasterBot
import tests.psgm_mocks as psgm_mocks
from unittest import mock

class TestMasterBot(unittest.TestCase):
    CFG = {
        'bots': [
            {
                "class_name": "bots.MasterBot", 
                "bot_name": "MasterBot", 
                "bot_id": "0", 
                "bot_url": "/masterbot", 
            }
        ]
    }

    @mock.patch('psgroupme.bots.base_bot.BotResponseManager', return_value=psgm_mocks.BotResponseManagerMock())
    def setUp(self, mock_brm):
        self.bot = MasterBot(self.CFG['bots'][0])
        self.bot.schedule = psgm_mocks.MOCK_SCHEDULE_1
        self.bot.player_stats = psgm_mocks.MockPlayerStats()

    def test_subclasses(self):
        for subclass in MasterBot.__bases__:
            self.assertIsInstance(self.bot, subclass)

    def test_build_context(self):
        context = self.bot.build_context()
        self.assertIsInstance(context, dict)
        self.assertIn('bot_name', context)
        self.assertIn('today', context)