import unittest
from psgroupme.bots.bot_responses import BotResponseManager


class TestBotResponses(unittest.TestCase):

    def setUp(self):
        self.brm = BotResponseManager(cfg_path='config/responses.example.yaml')
        pass

    def tearDown(self):
        pass

    def test_standard_responses_exists(self):
        global_responses = self.brm.get_global_responses()
        assert global_responses is not None
        assert type(global_responses) == list

    def test_standard_responses_matches_format(self):
        global_responses = self.brm.get_global_responses()
        for resp_item in global_responses:
            assert len(resp_item.items()) == 2
            assert 'input' in resp_item
            assert 'reply' in resp_item
