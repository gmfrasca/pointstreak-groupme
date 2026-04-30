from psgroupme.interfaces.clients import main as clients_main
import unittest
from unittest import mock

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
        }
    ],
    'img': {
        'dest': '/img/',
        'path': '/tmp'
    }
}


class TestClients(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @mock.patch('psgroupme.interfaces.clients.ClientManager')
    def test_app_runs(self, mock_client_manager_class):
        clients_main()
        mock_client_manager_class.assert_called_once_with(config_path=None)
        mock_client_manager_class.return_value.run.assert_called_once()
