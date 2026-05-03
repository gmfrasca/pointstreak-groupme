from psgroupme.interfaces.clients import main as clients_main
from psgroupme.interfaces.clients import FlaskClientManager, ClientManager, DiscordClientManager
from psgroupme.interfaces.listener import GroupmeListener, DiscordListener
import asyncio
import unittest
from unittest import mock
import yaml
import tempfile

EMPTY_CFG = {
    'clients': {
        'discord': {
            'token': 'FAKE_TOKEN'
        }
    },
    'bots': []
}


MOCK_CFG = {
    'clients': {
        'discord': {
            'token': 'FAKE_TOKEN'
        }
    },
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
        },
        {
            'class_name': 'bots.BaseBot',
            'bot_name': 'OtherBot',
            'listeners': [
                {
                    'type': 'groupme',
                    'url': '/schedulebot'
                },
                {
                    'type': 'discord',
                    'channel_id': '1234567890'
                }
            ]
        }
    ],
    'img': {
        'dest': '/img/',
        'path': '/tmp'
    }
}


class MockResponder(mock.MagicMock):
    pass

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


class TestClientManager(unittest.TestCase):

    def setUp(self):
        DiscordClientManager._instance = None
        DiscordClientManager._initialized = False

        self.config_path = tempfile.NamedTemporaryFile().name
        self.empty_config_path = tempfile.NamedTemporaryFile().name
        with open(self.config_path, 'w') as f:
            f.write(yaml.dump(MOCK_CFG))
        with open(self.empty_config_path, 'w') as f:
            f.write(yaml.dump(EMPTY_CFG))

    def tearDown(self):
        DiscordClientManager._instance = None
        DiscordClientManager._initialized = False

    @mock.patch('psgroupme.interfaces.clients.DiscordClientManager', return_value=mock.MagicMock())
    @mock.patch('psgroupme.interfaces.clients.FlaskClientManager.add_bot')
    @mock.patch('psgroupme.bots.BaseBot')
    def test_create_bots(self, mock_basebot_class, mock_fcm_add_bot, mock_discord_client_manager):
        cm = ClientManager(config_path=self.config_path)
        self.assertEqual(mock_fcm_add_bot.call_count, 2)
        cm.dcm.add_listener.assert_called_once()

    @mock.patch('psgroupme.interfaces.clients.DiscordClientManager', return_value=mock.MagicMock())
    @mock.patch('psgroupme.interfaces.clients.FlaskClientManager.add_bot')
    @mock.patch('psgroupme.interfaces.clients._thread.start_new_thread')
    @mock.patch('psgroupme.interfaces.clients.sleep', side_effect=KeyboardInterrupt)
    @mock.patch('psgroupme.bots.BaseBot')
    def test_run_with_discord(self, mock_basebot, mock_sleep, mock_start_thread, mock_fcm_add_bot, mock_dcm_class):
        cm = ClientManager(config_path=self.config_path)
        cm.run()
        thread_funcs = [call[0][0] for call in mock_start_thread.call_args_list]
        self.assertIn(cm.fcm.run, thread_funcs)
        self.assertIn(cm.dcm.run, thread_funcs)

    @mock.patch('psgroupme.interfaces.clients.FlaskClientManager.add_bot')
    @mock.patch('psgroupme.interfaces.clients._thread.start_new_thread')
    @mock.patch('psgroupme.interfaces.clients.sleep', side_effect=KeyboardInterrupt)
    def test_run_without_discord(self, mock_sleep, mock_start_thread, mock_fcm_add_bot):
        cm = ClientManager(config_path=self.empty_config_path)
        cm.dcm = None
        cm.run()
        self.assertEqual(mock_start_thread.call_count, 1)
        thread_funcs = [call[0][0] for call in mock_start_thread.call_args_list]
        self.assertIn(cm.fcm.run, thread_funcs)

    @mock.patch('psgroupme.interfaces.clients.FlaskClientManager.add_bot')
    @mock.patch('psgroupme.interfaces.clients._thread.start_new_thread', side_effect=Exception('thread error'))
    @mock.patch('psgroupme.interfaces.clients.sleep', side_effect=KeyboardInterrupt)
    def test_run_thread_start_failure(self, mock_sleep, mock_start_thread, mock_fcm_add_bot):
        cm = ClientManager(config_path=self.empty_config_path)
        cm.dcm = None
        with mock.patch('psgroupme.interfaces.clients.logging') as mock_logging:
            cm.run()
        mock_logging.error.assert_called()

    @mock.patch('psgroupme.interfaces.clients.discord.Client')
    @mock.patch('psgroupme.interfaces.clients.FlaskClientManager.add_bot')
    def test_add_listener(self, mock_fcm_add_bot, mock_discord_client):
        cm = ClientManager(config_path=self.empty_config_path)
        mock_basebot_class = mock.MagicMock()
        mock_dcm = mock.MagicMock()
        cm.dcm = mock_dcm

        # Test adding a groupme listener
        cm.fcm.add_bot.assert_not_called()
        cm.add_listener({'type': 'groupme', 'url': '/basebot'}, mock_basebot_class, '/basebot')
        cm.fcm.add_bot.assert_called_with(GroupmeListener, '/basebot', {'bot': mock_basebot_class})

        # Test adding a discord listener
        mock_dcm.add_listener.assert_not_called()
        cm.add_listener({'type': 'discord', 'channel_id': '1234567890'}, mock_basebot_class, '/basebot')
        mock_dcm.add_listener.assert_called_once()


class TestDiscordClientManager(unittest.TestCase):
    def setUp(self):
        DiscordClientManager._instance = None
        DiscordClientManager._initialized = False

        self.discord_client_manager = DiscordClientManager(config_path=None)
        self.discord_client_manager.discord_client = mock.MagicMock()
        self.discord_client_manager.discord_client.get_channel.return_value.send = mock.AsyncMock()
        self.discord_client_manager.listeners = []
        self.discord_client_manager._initialized = True
        self.discord_client_manager._logger = mock.MagicMock()

    def tearDown(self):
        DiscordClientManager._instance = None
        DiscordClientManager._initialized = False

    def test_add_listener(self):
        self.assertEqual(len(self.discord_client_manager.listeners), 0)
        self.discord_client_manager.add_listener(DiscordListener(mock.MagicMock(), '1234567890'))
        self.assertEqual(len(self.discord_client_manager.listeners), 1)

    def test_run(self):
        self.discord_client_manager.token = 'FAKE_TOKEN'
        self.discord_client_manager.run()
        self.discord_client_manager.discord_client.run.assert_called_once_with('FAKE_TOKEN')

    def test_send(self):
        with mock.patch('psgroupme.interfaces.clients.asyncio.run_coroutine_threadsafe',
                        side_effect=lambda coro, loop: asyncio.run(coro)):
            self.discord_client_manager.send('1234567890', 'Hello, world!')
        self.discord_client_manager.discord_client.get_channel.assert_called_once_with('1234567890')
        self.discord_client_manager.discord_client.get_channel.return_value.send.assert_called_once_with('Hello, world!')

    def test_send_image(self):
        with mock.patch('psgroupme.interfaces.clients.asyncio.run_coroutine_threadsafe',
                        side_effect=lambda coro, loop: asyncio.run(coro)):
            self.discord_client_manager.send('1234567890', 'https://tenor.com/view/cat-gif-cat-computer-cat-funny-gif-gif-21234567890')
        self.discord_client_manager.discord_client.get_channel.assert_called_once_with('1234567890')
        self.discord_client_manager.discord_client.get_channel.return_value.send.assert_called_once_with('https://tenor.com/view/cat-gif-cat-computer-cat-funny-gif-gif-21234567890')

    def test_send_remote_image_url(self):
        """Image URL from a non-local domain → embed-only send (no file attachment)."""
        url = 'https://example.com/image.jpg'
        channel_send = self.discord_client_manager.discord_client.get_channel.return_value.send
        with mock.patch('psgroupme.interfaces.clients.asyncio.run_coroutine_threadsafe',
                        side_effect=lambda coro, loop: asyncio.run(coro)):
            self.discord_client_manager.send('1234567890', url)
        self.discord_client_manager.discord_client.get_channel.assert_called_once_with('1234567890')
        channel_send.assert_called_once()
        _, kwargs = channel_send.call_args
        self.assertIn('embed', kwargs)
        self.assertNotIn('file', kwargs)

    @mock.patch('psgroupme.interfaces.clients.discord.File')
    @mock.patch('psgroupme.interfaces.clients.requests.get')
    def test_send_local_image_url(self, mock_requests_get, mock_discord_file):
        """Image URL from a local domain (tenor.com) → download, attach as file, embed send."""
        url = 'https://tenor.com/cat.gif'
        mock_requests_get.return_value.content = b'fake_image_data'
        mock_discord_file.return_value.filename = 'cat.gif'
        channel_send = self.discord_client_manager.discord_client.get_channel.return_value.send
        with mock.patch('psgroupme.interfaces.clients.asyncio.run_coroutine_threadsafe',
                        side_effect=lambda coro, loop: asyncio.run(coro)):
            self.discord_client_manager.send('1234567890', url)
        self.discord_client_manager.discord_client.get_channel.assert_called_once_with('1234567890')
        mock_requests_get.assert_called_once_with(url)
        channel_send.assert_called_once()
        _, kwargs = channel_send.call_args
        self.assertIn('file', kwargs)
        self.assertIn('embed', kwargs)


class TestFlaskClientManager(unittest.TestCase):    
    def setUp(self):
        self.flask_client_manager = FlaskClientManager(config_path=None)
        self.flask_client_manager._logger = mock.MagicMock()
        
    def tearDown(self):
        pass

    @mock.patch('flask_restful.Api.add_resource')
    def test_add_bot(self, mock_add_resource):
        self.flask_client_manager.add_bot(MockResponder, '/bot', {'bot': 'bot'})
        mock_add_resource.assert_called_once()

    @mock.patch('flask.Flask.run')
    def test_run(self, mock_flask_run):
        self.flask_client_manager.run()
        mock_flask_run.assert_called_once()


