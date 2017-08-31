from psgroupme.rest import main as rest_main
import unittest
import mock


class TestRest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @mock.patch('psgroupme.rest.Flask.run')
    def test_app_runs(self, mock_flask_runner):
        rest_main()
        mock_flask_runner.assert_called_once()
