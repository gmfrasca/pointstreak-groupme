import psgroupme.bot_responses as br
import unittest


class TestBotResponses(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_standard_responses_exists(self):
        assert br.GLOBAL_RESPONSES is not None
        assert type(br.GLOBAL_RESPONSES) == list

    def test_standard_responses_matches_format(self):
        for resp_item in br.GLOBAL_RESPONSES:
            assert len(resp_item.items()) == 2
            assert 'input' in resp_item
            assert 'reply' in resp_item
