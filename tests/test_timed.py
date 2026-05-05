import unittest
from unittest import mock
import tempfile
from psgroupme.interfaces.timed import main as timed_main, str_to_class
from psgroupme.bots.timed.timed_ping_bot import TimedPingBot
import yaml

MOCK_CFG = {
    'bots': []
}

MOCK_CFG_WITH_BOTS = {
    'bots': [
        {
            'class_name': 'bots.TimedPingBot',
        }
    ]
}

class TestTimed(unittest.TestCase):
    def setUp(self):
        self.config_path = tempfile.NamedTemporaryFile().name
        self.config_path_with_bots = tempfile.NamedTemporaryFile().name
        with open(self.config_path, 'w') as f:
            f.write(yaml.dump(MOCK_CFG))
        with open(self.config_path_with_bots, 'w') as f:
            f.write(yaml.dump(MOCK_CFG_WITH_BOTS))

    def tearDown(self):
        pass

    @mock.patch('psgroupme.interfaces.timed.signal.pause', side_effect=KeyboardInterrupt)
    def test_main_no_bots(self, mock_signal_pause):
        timed_main(self.config_path)
        mock_signal_pause.assert_called_once()

    @mock.patch('psgroupme.interfaces.timed.signal.pause', side_effect=KeyboardInterrupt)
    def test_main_with_bots(self, mock_signal_pause):
        mock_bot_class = mock.MagicMock()
        with mock.patch('psgroupme.interfaces.timed.str_to_class', return_value=mock_bot_class):
            timed_main(self.config_path_with_bots)
        mock_bot_class.assert_called_once()
        mock_bot_class.return_value.start.assert_called_once()
        mock_bot_class.return_value.stop.assert_called_once()
        
    def test_str_to_class(self):
        self.assertEqual(str_to_class('bots.TimedPingBot'), TimedPingBot)
