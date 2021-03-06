import unittest
import mock
import json
import psgroupme
import yaml
from psgroupme.bots import BaseBot, ScheduleBot, BotResponseManager
from recleagueparser.schedules.pointstreak_schedule import \
    PointstreakSchedule

EXAMPLE_RESP_YAML = 'config/responses.example.yaml'

BOTNAMES = {
    'BaseBot': 'BaseBot',
    'ScheduleBot': 'TestBot',
}

MOCK_CFG = {
            'bots': [
                {
                     'class_name': 'bots.BaseBot',
                     'bot_name': BOTNAMES['BaseBot'],
                     'bot_id': '0',
                     'bot_url': '/basebot',
                },
                {
                     'class_name': 'bots.ScheduleBot',
                     'bot_name': BOTNAMES['ScheduleBot'],
                     'bot_id': '1',
                     'bot_url': '/schedulebot',
                }
            ]
        }

MOCK_RESP_CFG = '''
extra_context:
       github_url: 'https://github.com/gmfrasca/pointstreak-groupme'
responses:
  global:
    - input: '(hi|hello|greetings|salutations|sup),? {bot_name}'
      reply: 'Hello, {name}'
    - input: 'show me the (source|sauce|src|code)'
      reply: 'You can find it at {github_url}'
    - input: '(what|who) is (a )? {bot_name}'
      reply: 'I am a GroupMe helper bot, beep boop. More info at {github_url}'
  schedulebot:
    - input: 'when.*next game([\?\!\.( is)].*)??$'
      action: load_schedule
      reply: '{nextgame_resp}'
    - input: 'what was the score\??'
      action: load_schedule
      reply: '{lastgame_resp}'
    - input: "^how('d| did)? we do([\\\?\\\!\\\.].*)??$"
      action: load_schedule
      reply: '{lastgame_resp}'
    - input: 'what is.* schedule([\?\!\.].*)??$'
      action: load_schedule
      reply: '{schedule_resp}'
    - input: '^how many do we have'
      action: load_rsvp
      reply: '{attendance_resp}'
    - input: 'what is today'
      reply: '{today}'
    - input: '!nextgame'
      action: load_schedule
      reply: '{next_game}'
    - input: '!lastgame'
      action: load_schedule
      reply: '{last_game}'
    - input: '!schedule'
      action: load_schedule
      reply: '{schedule}'
    - input: '!attendance'
      action: load_rsvp
      reply: '{attendance}'
    - input: '!source'
      reply: '{github_url}'
    - input: '!today'
      reply: '{today}'
    - input: '!help'
      reply: >
              Available Commands - !nextgame, !lastgame, !schedule, !attendance,
              !source, !today, !help

'''  # noqa


class BotResponseManagerMock(BotResponseManager):

    def reload_data(self):
        self.data = yaml.load(MOCK_RESP_CFG, Loader=yaml.FullLoader)
        return MOCK_RESP_CFG


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

    def get_next_game_attendees(self):
        return "NextGameAttendees"

    def get_next_game_lines(self):
        return "NextGameLines"

    def get_team_fee_progress(self):
        return "TeamFeeProgress"


class TestBaseBot(unittest.TestCase):

    @mock.patch('psgroupme.bots.base_bot.BotResponseManager')
    def setUp(self, mock_brm):
        bot_id = 0
        mock_cfg = MOCK_CFG['bots'][bot_id]
        self.bot = BaseBot(mock_cfg)
        self.bot.brm = BotResponseManagerMock()

    def tearDown(self):
        pass

    def test_get_request(self):
        expected = dict(bot_cfg=self.bot.bot_data)
        self.assertEqual(self.bot.get(), expected)

    @mock.patch("psgroupme.bots.base_bot.request")
    def test_post_request(self, mocked_data):
        mocked_data.data = '{"foo": "bar"}'
        loaded_dict = json.loads(mocked_data.data)
        expected = dict(post=loaded_dict)
        self.bot.handle_msg = mock.MagicMock()
        self.assertEqual(self.bot.post(), expected)
        self.bot.handle_msg.assert_called_once_with(loaded_dict)

    @mock.patch("psgroupme.bots.base_bot.request")
    def test_bad_post_request(self, mocked_data):
        mocked_data.data = '{"this_is_bad_json'
        self.bot.handle_msg = mock.MagicMock()
        self.assertEqual(self.bot.post(), None)
        self.bot.handle_msg.assert_not_called()

    @mock.patch.object(psgroupme.bots.base_bot.Responder, 'reply')
    def test_respond(self, reply_fn):
        self.bot.respond("foobar")
        reply_fn.assert_called_once_with('foobar')

    def test_includes_standard_replies(self):
        self.bot.refresh_responses()
        brm = BotResponseManager(cfg_path=EXAMPLE_RESP_YAML)
        for resp_item in brm.get_global_responses():
            assert resp_item in self.bot.responses

    def test_excludes_specialized_replies(self):
        self.bot.refresh_responses()
        brm = BotResponseManager(cfg_path=EXAMPLE_RESP_YAML)
        for resp_item in brm.get_responses().get('base', list()):
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
        self.bot.get_params = mock.MagicMock()
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
        self.bot.refresh_responses.assert_called_once()

        test_msg = dict(text='foobar')
        self.bot.read_msg(test_msg)
        self.bot.respond.assert_called_with(['helloworld'])
        self.bot.refresh_responses.assert_called()

        test_msg = dict(text='1test2')
        self.bot.read_msg(test_msg)
        self.bot.respond.assert_called_with(['testregex'])
        self.bot.refresh_responses.assert_called()

        test_msg = dict(text='format_test')
        self.bot.read_msg(test_msg)
        self.bot.respond.assert_called_with([BOTNAMES[self.bot.bot_type]])
        self.bot.refresh_responses.assert_called()


class TestScheduleBot(TestBaseBot):

    @mock.patch('psgroupme.bots.base_bot.BotResponseManager')
    def setUp(self, mock_brm):
        bot_id = 1
        mock_cfg = MOCK_CFG['bots'][bot_id]
        self.mock_tlr = TeamLockerRoomMock()
        self.mock_sched = PointstreakScheduleMock()
        self.bot = ScheduleBot(mock_cfg, schedule=self.mock_sched,
                               rsvp=self.mock_tlr)
        self.bot.brm = BotResponseManagerMock()

    def test_includes_specialized_replies(self):
        self.bot.refresh_responses()
        brm = BotResponseManager(cfg_path=EXAMPLE_RESP_YAML)
        for resp in brm.get_responses().get('schedulebot', []):
            found = False
            for actual in self.bot.responses:
                if actual.get('input') == resp.get('input') and \
                   resp.get('reply') == actual.get('reply'):
                    found = True
                    break
            assert found

    @mock.patch.object(psgroupme.bots.base_bot.Responder, 'reply')
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
                self.bot.read_msg(test_msg)
                if dialog[1]:
                    mock_resp.assert_called_with([dialog[1]])
                else:
                    mock_resp.assert_not_called()
