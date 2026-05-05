from psgroupme.__main__ import main
import unittest
from unittest import mock
import logging
from psgroupme.interfaces.clients import main as start_client_bots
from psgroupme.interfaces.timed import main as start_timed_bots


class TestMain(unittest.TestCase):

    @mock.patch('psgroupme.__main__._thread')
    @mock.patch('argparse.ArgumentParser.parse_args')
    @mock.patch('psgroupme.__main__.sleep', side_effect=KeyboardInterrupt)
    def test_main(self, mock_sleep, mock_parse_args, mock_thread):
        main()
        mock_thread.start_new_thread.assert_any_call(start_client_bots, ())
        mock_thread.start_new_thread.assert_any_call(start_timed_bots, ())

    @mock.patch('psgroupme.__main__._thread')
    @mock.patch('psgroupme.interfaces.clients.logging')
    @mock.patch('argparse.ArgumentParser.parse_args')
    @mock.patch('psgroupme.__main__.sleep', side_effect=KeyboardInterrupt)
    def test_main_with_exception(self, mock_sleep, mock_parse_args, mock_logging, mock_thread):
        mock_thread.start_new_thread.side_effect = Exception("Test Exception")
        with self.assertLogs(logging.getLogger(), level="ERROR") as cm:
            main()
            self.assertIn("Unable to start thread", cm.output[0])
            self.assertIn("Test Exception", cm.output[1])
