import psgroupme
from psgroupme.bots import BaseBot, ScheduleBot, HockeyBot
from psgroupme.bot_responses import GLOBAL_RESPONSES, SCHEDULE_BOT_RESPONSES
from psgroupme.team_schedule import PointstreakSchedule
import unittest
import mock
import json


BOTNAMES = {
    'BaseBot': 'BaseBot',
    'ScheduleBot': 'TestBot',
    'HockeyBot': 'HockeyBot'
}

MOCK_CFG = {
            'bots': [
                {
                     'class_name': 'bots.BaseBot',
                     'bot_name': BOTNAMES['BaseBot'],
                     'bot_id': '0',
                     'bot_url': '/basebot',
                     'group_name': 'foo',
                     'group_id': '12345',
                     'callback_url': 'http://foo.bar',
                     'avatar_url': 'http://funny.jpg'
                },
                {
                     'class_name': 'bots.ScheduleBot',
                     'bot_name': BOTNAMES['ScheduleBot'],
                     'bot_id': '1',
                     'bot_url': '/schedulebot',
                     'group_name': 'foo',
                     'group_id': '12345',
                     'callback_url': 'http://foo.bar',
                     'avatar_url': 'http://funny.jpg'
                },
                {
                      'class_name': 'bots.HockeyBot',
                      'bot_name': BOTNAMES['HockeyBot'],
                      'bot_id': '2',
                      'bot_url': '/hockeybot',
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
        self.games = [self.get_last_game_before(),
                      self.get_next_game_after()]

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


class TeamLockerRoomMock(object):

    def get_next_game_attendance(self):
        return "NextGameAttendance"


class TestBaseBot(unittest.TestCase):

    @mock.patch.object(psgroupme.config_manager.ConfigManager,
                       'get_bot_data_by_id')
    @mock.patch.object(psgroupme.config_manager.ConfigManager, 'load_cfg')
    def setUp(self, mock_load, mock_load_id):
        bot_id = 0
        mock_load_id.return_value = MOCK_CFG['bots'][bot_id]
        self.bot = BaseBot(bot_id)
        print(self.bot.cfg_mgr.load_cfg().get('bots'))

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
            type(self.bot).__name__))

    def test_includes_standard_replies(self):
        self.bot.refresh_responses()
        for resp_item in GLOBAL_RESPONSES:
            assert resp_item in self.bot.responses

    def test_excludes_specialized_replies(self):
        self.bot.refresh_responses()
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
        self.bot.refresh_responses = mock.MagicMock()
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
        self.bot.refresh_responses.assert_not_called()

        test_msg = dict(text='foobar')
        self.bot.read_msg(test_msg)
        self.bot.respond.assert_called_with('helloworld')
        self.bot.refresh_responses.assert_called()

        test_msg = dict(text='1test2')
        self.bot.read_msg(test_msg)
        self.bot.respond.assert_called_with('testregex')
        self.bot.refresh_responses.assert_called()

        print(self.bot.bot_data)
        test_msg = dict(text='format_test')
        self.bot.read_msg(test_msg)
        self.bot.respond.assert_called_with('{}'.format(
            BOTNAMES[self.bot.bot_type]))
        self.bot.refresh_responses.assert_called()


class TestScheduleBot(TestBaseBot):

    @mock.patch.object(psgroupme.config_manager.ConfigManager,
                       'get_bot_data_by_id')
    @mock.patch.object(psgroupme.config_manager.ConfigManager, 'load_cfg')
    def setUp(self, mock_load, mock_load_id):
        bot_id = 1
        mock_load_id.return_value = MOCK_CFG['bots'][bot_id]
        self.mock_tlr = TeamLockerRoomMock()
        self.mock_sched = PointstreakScheduleMock()
        self.bot = ScheduleBot(bot_id, schedule=self.mock_sched,
                               tlr=self.mock_tlr)

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
        nextgame_resp = self.bot.NEXTGAME_RESPONSE.format('TestNextGame')
        lastgame_resp = self.bot.LASTGAME_RESPONSE.format('TestLastGame')
        schedule_resp = self.bot.SCHEDULE_RESPONSE.format('TestSchedule')
        bot_name = BOTNAMES[self.bot.bot_type]

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
                print(test_msg)
                self.bot.read_msg(test_msg)
                if dialog[1]:
                    mock_resp.assert_called_with(dialog[1])
                else:
                    mock_resp.assert_not_called()


class TestHockeyBot(TestScheduleBot):
    """Just a clone of ScheduleBot, with a different bot name"""

    @mock.patch.object(psgroupme.config_manager.ConfigManager,
                       'get_bot_data_by_id')
    @mock.patch.object(psgroupme.config_manager.ConfigManager, 'load_cfg')
    def setUp(self, mock_load, mock_load_id):
        bot_id = 2
        mock_load_id.return_value = MOCK_CFG['bots'][bot_id]
        self.mock_sched = PointstreakScheduleMock()
        self.mock_tlr = TeamLockerRoomMock()
        self.bot = HockeyBot(bot_id, schedule=self.mock_sched,
                             tlr=self.mock_tlr)

    def test_bot_name(self):
        self.assertNotEqual(self.bot.bot_type, ScheduleBot.__name__)
