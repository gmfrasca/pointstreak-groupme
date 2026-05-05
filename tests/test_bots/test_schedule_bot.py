import psgroupme
from unittest import mock
from psgroupme.bots.schedule_bot import ScheduleBot
from psgroupme.bots.bot_responses import BotResponseManager
from tests.psgm_mocks import MOCK_CFG, EXAMPLE_RESP_YAML, BOTNAMES
from tests.psgm_mocks import PointstreakScheduleMock, TeamLockerRoomMock
from psgroupme.bots.schedule_bot import ScheduleBot
from tests.test_bots.test_base_bot import TestBaseBot, BotResponseManagerMock


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