import psgroupme
from psgroupme.bots import BaseBot, ScheduleBot, HockeyBot
from psgroupme.bot_responses import GLOBAL_RESPONSES, SCHEDULE_BOT_RESPONSES
from psgroupme.team_schedule import PointstreakSchedule
import unittest
import mock
import json


MOCK_CFG = {
            'bots': [
                {
                     'bot_name': 'BaseBot',
                     'bot_id': '1',
                     'group_name': 'foo',
                     'group_id': '12345',
                     'callback_url': 'http://foo.bar',
                     'avatar_url': 'http://funny.jpg'
                },
                {
                     'bot_name': 'TestBot',
                     'bot_id': '2',
                     'group_name': 'foo',
                     'group_id': '12345',
                     'callback_url': 'http://foo.bar',
                     'avatar_url': 'http://funny.jpg'
                },
                {
                      'bot_name': 'HockeyBot',
                      'bot_id': '3',
                      'group_name': 'foo',
                      'group_id': '12345',
                      'callback_url': 'http://foo.bar',
                      'avatar_url': 'http://funny.jpg'
                }
            ]
        }


class PointstreakScheduleMock(PointstreakSchedule):

    def __init__(self, *args, **kwargs):
        self.html_table = mock.MagicMock()
        self.games = mock.MagicMock()

    def __repr__(self):
        return 'TestSchedule'

    def refresh_schedule(self):
        return

    def retrieve_html_table(self, *args, **kwargs):
        return 'TestHtml'

    def parse_table(self, *args, **kwargs):
        return 'TestParsedTable'

    def parse_team(self, *args, **kwargs):
        return 'TestTeam', 5

    def get_next_game_after(self, *args, **kwargs):
        return 'TestNextGame'

    def get_last_game_before(self, *args, **kwargs):
        return 'TestLastGame'


class TestBaseBot(unittest.TestCase):

    @mock.patch.object(psgroupme.config_manager.ConfigManager, 'load_cfg')
    def setUp(self, mock_cfg_mgr_load):
        mock_cfg_mgr_load.return_value = MOCK_CFG
        self.bot = BaseBot()

    def tearDown(self):
        pass

    def test_get_request(self):
        expected = dict(bot_cfg=self.bot.bot_data)
        self.assertEqual(self.bot.get(), expected)

    @mock.patch("psgroupme.bots.request")
    def test_post_request(self, mocked_data):
        mocked_data.data = '{"foo": "bar"}'
        loaded_dict = json.loads(mocked_data.data)
        expected = dict(post=loaded_dict)
        self.bot.handle_msg = mock.MagicMock()
        self.assertEqual(self.bot.post(), expected)
        self.bot.handle_msg.assert_called_once_with(loaded_dict)

    @mock.patch("psgroupme.bots.request")
    def test_bad_post_request(self, mocked_data):
        mocked_data.data = '{"this_is_bad_json'
        self.bot.handle_msg = mock.MagicMock()
        self.assertEqual(self.bot.post(), None)
        self.bot.handle_msg.assert_not_called()

    @mock.patch.object(psgroupme.responder.Responder, 'reply')
    def test_respond(self, reply_fn):
        self.bot.respond("foobar")
        reply_fn.assert_called_once_with('Hello, this is {0}'.format(
            self.bot.BOT_NAME))

    def test_includes_standard_replies(self):
        for resp_item in GLOBAL_RESPONSES:
            assert resp_item in self.bot.responses

    def test_excludes_specialized_replies(self):
        for resp_item in SCHEDULE_BOT_RESPONSES:
            assert resp_item not in self.bot.responses

    def test_handle_msg(self):
        self.bot.read_msg = mock.MagicMock()
        test_msg = {
            'text': 'I am a user message',
            'system': False,
            'sender_type': 'user'
        }
        self.bot.handle_msg(test_msg)
        self.bot.read_msg.assert_called_once()

    def test_ignore_system_msg(self):
        self.bot.read_msg = mock.MagicMock()
        test_msg = {
            'text': 'I am a system message',
            'system': True,
            'sender_type': 'user'
        }
        self.bot.handle_msg(test_msg)
        self.bot.read_msg.assert_not_called()

    def test_ignore_bot_msg(self):
        self.bot.read_msg = mock.MagicMock()
        test_msg = {
            'text': 'I am a bot message',
            'system': False,
            'sender_type': 'bot'
        }
        self.bot.handle_msg(test_msg)
        self.bot.read_msg.assert_not_called()

    def test_read_msg(self):
        self.bot.respond = mock.MagicMock()
        self.bot.responses = [
            {
                'input': r'foobar',
                'reply': 'helloworld'
            },
            {
                'input': r'[0-9]test[0-9]',
                'reply': 'testregex'
            },
            {
                'input': r'format_test',
                'reply': '{bot_name}'
            }
        ]

        test_msg = dict(text='ignore_me')
        self.bot.read_msg(test_msg)
        self.bot.respond.assert_not_called()

        test_msg = dict(text='foobar')
        self.bot.read_msg(test_msg)
        self.bot.respond.assert_called_with('helloworld')

        test_msg = dict(text='1test2')
        self.bot.read_msg(test_msg)
        self.bot.respond.assert_called_with('testregex')

        test_msg = dict(text='format_test')
        self.bot.read_msg(test_msg)
        self.bot.respond.assert_called_with('{}'.format(self.bot.BOT_NAME))


class TestScheduleBot(TestBaseBot):

    @mock.patch.object(psgroupme.config_manager.ConfigManager, 'load_cfg')
    def setUp(self, mock_cfg_mgr_load):
        mock_cfg_mgr_load.return_value = MOCK_CFG
        self.mock_sched = PointstreakScheduleMock()
        self.bot = ScheduleBot(schedule=self.mock_sched)

    def test_includes_specialized_replies(self):
        for resp_item in SCHEDULE_BOT_RESPONSES:
            assert resp_item in self.bot.responses

    @mock.patch.object(psgroupme.responder.Responder, 'reply')
    def test_respond(self, reply_fn):
        test_msg = 'foobar'
        self.bot.respond(test_msg)
        reply_fn.assert_called_once_with(test_msg)

    def test_excludes_specialized_replies(self):
        pass

    @mock.patch.object(psgroupme.bots.ScheduleBot, 'respond')
    def test_real_responses(self, mock_resp):
        # Canned responses
        nextgame_resp = 'TestNextGame'
        lastgame_resp = 'TestLastGame'
        schedule_resp = 'TestSchedule'
        bot_name = self.bot.BOT_NAME

        username = 'TestUser'
        context = dict(name=username, system=False, sender_type='user')
        test_msg_list = [
            ('Hello, {0}'.format(bot_name), 'Hello, {0}'.format(username)),
            ('abc', None),
            ('Does anyone know when the next game is', nextgame_resp),
            ('When the f is the next game', nextgame_resp),
            ('next game', None),
            ('how did we do', lastgame_resp),
            ('HoW dId We Do?', lastgame_resp),
            ('HoW dId We Do? blah blah blah', lastgame_resp),
            ('did we do', None),
            ('how\'d we do?', lastgame_resp),
            ('how we do', lastgame_resp),
            ('how we do it', None),
            ('this is how we do it', None),
            ('what was the score', lastgame_resp),
            ('what was the score, {0}'.format(bot_name), lastgame_resp),
            ('what is schedule', schedule_resp),
            ('what is scheduled', None),
            ('what is the schedule', schedule_resp)
        ]
        for dialog in test_msg_list:
            with mock.patch.object(psgroupme.bots.ScheduleBot,
                                   'respond') as mock_resp:
                test_msg = dict(text=dialog[0])
                test_msg.update(context)
                self.bot.read_msg(test_msg)
                if dialog[1]:
                    mock_resp.assert_called_with(dialog[1])
                else:
                    mock_resp.assert_not_called()


class TestHockeyBot(TestScheduleBot):
    """Just a clone of ScheduleBot, with a different bot name"""

    @mock.patch.object(psgroupme.config_manager.ConfigManager, 'load_cfg')
    def setUp(self, mock_cfg_mgr_load):
        mock_cfg_mgr_load.return_value = MOCK_CFG
        self.mock_sched = PointstreakScheduleMock()
        self.bot = HockeyBot(schedule=self.mock_sched)

    def test_bot_name(self):
        assert self.bot.BOT_NAME
