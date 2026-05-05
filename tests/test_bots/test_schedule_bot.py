import psgroupme
from unittest import mock
from psgroupme.bots.schedule_bot import ScheduleBot
from psgroupme.bots.bot_responses import BotResponseManager
from tests.psgm_mocks import MOCK_CFG, EXAMPLE_RESP_YAML, BOTNAMES
from tests.psgm_mocks import PointstreakScheduleMock, TeamLockerRoomMock
import tests.psgm_mocks as psgm_mocks
from psgroupme.bots.schedule_bot import ScheduleBot
from tests.test_bots.test_base_bot import TestBaseBot, BotResponseManagerMock
from recleagueparser.schedules.dashplatform_schedule import DashPlatformSchedule
from recleagueparser.schedules.pointstreak_schedule import PointstreakSchedule
from recleagueparser.schedules.sportsengine_schedule import SportsEngineSchedule
from recleagueparser.schedules.ics_schedule import ICSSchedule


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

    #TODO: Use generic responder instead of GroupmeResponder
    @mock.patch.object(psgroupme.interfaces.responder.GroupmeResponder, 'reply')
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
        context = dict(name=username, bot_name=bot_name,system=False, sender_type='user')
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


    @mock.patch('recleagueparser.schedules.schedule_factory.ScheduleFactory.create')
    def test_load_schedule(self, mock_create):
        self.bot.schedule = None
        self.bot.bot_data = {'schedule': {'type': 'dash', 'team_id': 0, 'company_id': 0}}
        self.bot.load_schedule()
        mock_create.assert_called_with(type='dash', schedule_type='dash', team_id=0, company_id=0)

        self.bot.schedule = None
        self.bot.bot_data = {'schedule': {'type': 'pointstreak', 'team_id': 0, 'season_id': 0}}
        self.bot.load_schedule()
        mock_create.assert_called_with(type='pointstreak', schedule_type='pointstreak', team_id=0, season_id=0)
        
        self.bot.schedule = None
        self.bot.bot_data = {'schedule': {'type': 'sportsengine', 'team_id': 0, 'season_id': 0}}
        self.bot.load_schedule()
        mock_create.assert_called_with(type='sportsengine', schedule_type='sportsengine', team_id=0, season_id=0)
        
        self.bot.schedule = None
        self.bot.bot_data = {'schedule': {'type': 'ics', 'team_id': 0, 'season_id': 0}}
        self.bot.load_schedule()
        mock_create.assert_called_with(type='ics', schedule_type='ics', team_id=0, season_id=0)


    @mock.patch('recleagueparser.schedules.schedule_factory.ScheduleFactory.create')
    def test_load_compare_schedule(self, mock_create):
        self.bot.compare_schedule = None
        self.bot.bot_data = {'compare_schedule': {'type': 'dash', 'team_id': 0, 'company_id': 0}}
        self.bot._load_compare_schedule()
        mock_create.assert_called_with(type='dash', schedule_type='dash', team_id=0, company_id=0)

        self.bot.compare_schedule = None
        self.bot.bot_data = {'compare_schedule': {'type': 'pointstreak', 'team_id': 0, 'season_id': 0}}
        self.bot._load_compare_schedule()
        mock_create.assert_called_with(type='pointstreak', schedule_type='pointstreak', team_id=0, season_id=0)
        
        self.bot.compare_schedule = None
        self.bot.bot_data = {'compare_schedule': {'type': 'sportsengine', 'team_id': 0, 'season_id': 0}}
        self.bot._load_compare_schedule()
        mock_create.assert_called_with(type='sportsengine', schedule_type='sportsengine', team_id=0, season_id=0)
        
        self.bot.compare_schedule = None
        self.bot.bot_data = {'compare_schedule': {'type': 'ics', 'team_id': 0, 'season_id': 0}}
        self.bot._load_compare_schedule()
        mock_create.assert_called_with(type='ics', schedule_type='ics', team_id=0, season_id=0)


    @mock.patch.object(psgroupme.bots.ScheduleBot, 'respond')
    @mock.patch('recleagueparser.schedules.compare.ScheduleComparer')
    def test_compare_schedules(self, mock_sc, mock_resp):

        mock_schedule = psgm_mocks.MOCK_SCHEDULE_1
        self.bot.schedule = mock_schedule
        self.bot.compare_schedule = mock_schedule

        self.bot.compare_schedules('test message')
        mock_resp.assert_called_with('Schedule syncronization verified: no diffs detected')

        self.bot.schedule = psgm_mocks.MOCK_EMPTY_SCHEDULE
        self.bot.compare_schedule = psgm_mocks.MOCK_SCHEDULE_2
        self.bot.compare_schedules('test message')
        mock_resp.assert_called_with('Schedule Diff Detected:\n+ TestHomeTeam vs TestAwayTeam2 at Sat, May 04 10:00 AM\n')