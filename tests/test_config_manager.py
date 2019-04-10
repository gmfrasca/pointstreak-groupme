from psgroupme.config_manager import ConfigManager
import unittest
import mock


class TestConfigManager(unittest.TestCase):

    MOCK_YAML = '''
bots:
    - class_name: 'foo'
      bot_name: 'bar'
      bot_id: '12345'
      group_name: 'foo'
      group_id: '12345'
      callback_url: 'http://foo.bar'
      avatar_url: 'http://funny.jpg'
'''

    def setUp(self):
        with mock.patch('__builtin__.open',
                        mock.mock_open(read_data=self.MOCK_YAML)):
            assert open('/fake/config.yaml').read() == self.MOCK_YAML
            self.cfg_mgr = ConfigManager()

    def tearDown(self):
        pass

    def test_load_config(self):
        expected = {
            'bots': [
                {
                     'class_name': 'foo',
                     'bot_name': 'bar',
                     'bot_id': '12345',
                     'group_name': 'foo',
                     'group_id': '12345',
                     'callback_url': 'http://foo.bar',
                     'avatar_url': 'http://funny.jpg'
                 }
            ]
        }
        self.assertEqual(expected, self.cfg_mgr.cfg)

    def test_get_bot_data(self):
        expected = {
            'class_name': 'foo',
            'bot_name': 'bar',
            'bot_id': '12345',
            'group_name': 'foo',
            'group_id': '12345',
            'callback_url': 'http://foo.bar',
            'avatar_url': 'http://funny.jpg'
        }
        print(self.cfg_mgr.cfg)
        self.assertEqual(self.cfg_mgr.get_bot_data('foo'), expected)

    def test_get_bot_data_no_config(self):
        self.assertEqual(self.cfg_mgr.get_bot_data('nothere'), dict())

    def test_get_bot_id(self):
        self.assertEqual(self.cfg_mgr.get_bot_id('foo'), '12345')

    def test_get_bot_id_no_config(self):
        self.assertEqual(self.cfg_mgr.get_bot_id('nothere'), None)
