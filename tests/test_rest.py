from psgroupme.interfaces.rest import main as rest_main
import unittest
import mock

MOCK_CFG = {
            'bots': [
                {
                     'class_name': 'bots.BaseBot',
                     'bot_name': 'BaseBot',
                     'bot_id': '0',
                     'bot_url': '/basebot',
                     'group_name': 'foo',
                     'group_id': '12345',
                     'callback_url': 'http://foo.bar',
                     'avatar_url': 'http://funny.jpg'
                }]
           }


class TestRest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @mock.patch('psgroupme.interfaces.rest.Flask.run')
    @mock.patch('psgroupme.interfaces.rest.ConfigManager')
    def test_app_runs(self, mock_cm, mock_flask_runner):
        mock_cm.get_bots.return_value = MOCK_CFG['bots']
        rest_main()
        mock_flask_runner.assert_called_once()
