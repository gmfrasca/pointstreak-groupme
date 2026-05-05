import mock
import yaml
from psgroupme.bots import BotResponseManager
from recleagueparser.schedules.pointstreak_schedule import \
    PointstreakSchedule
from recleagueparser.schedules.game import Game
from recleagueparser.schedules.schedule import Schedule

EXAMPLE_RESP_YAML = 'tests/config/responses.example.yaml'

BOTNAMES = {
    'BaseBot': 'BaseBot',
    'ScheduleBot': 'TestBot',
}

MOCK_CFG = {
            'bots': [
                {
                     'responders': [
                        {
                            'type': 'groupme',
                            'bot_id': '0'
                        }
                     ],
                     'listeners': [
                        {
                            'type': 'groupme',
                            'url': '/basebot'
                        }
                     ],
                     'bot_name': BOTNAMES['BaseBot'],
                },
                {
                     'responders': [
                        {
                            'type': 'groupme',
                            'bot_id': '1'
                        }
                     ],
                     'listeners': [
                        {
                            'type': 'groupme',
                            'url': '/schedulebot'
                        }
                     ],
                     'bot_name': BOTNAMES['ScheduleBot'],
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


# Mock Games
MOCK_GAME_1 = Game(date='Sun, May 03 2126', time='10:00', hometeam='TestHomeTeam', awayteam='TestAwayTeam', homescore=1, awayscore=2)
MOCK_GAME_2 = Game(date='Mon, May 04 2126', time='10:00', hometeam='TestHomeTeam', awayteam='TestAwayTeam2', homescore=5, awayscore=0)


# Mock Schedules
class MockSchedule(Schedule):
    def get_schedule_url(self, *args, **kwargs):
        return 'https://example.com'

    def parse_table(self, *args, **kwargs):
        return self.games

    def retrieve_html_table(self, *args, **kwargs):
        return 'TestHtml'

MOCK_EMPTY_SCHEDULE = MockSchedule(team_id=0)
MOCK_SCHEDULE_1 = MockSchedule(team_id=0)
MOCK_SCHEDULE_2 = MockSchedule(team_id=0)
MOCK_SCHEDULE_1.games = [MOCK_GAME_1, MOCK_GAME_2]
MOCK_SCHEDULE_2.games = [MOCK_GAME_2]


class TeamLockerRoomMock(object):

    def get_next_game_attendance(self):
        return "NextGameAttendance"

    def get_next_game_attendees(self):
        return "NextGameAttendees"

    def get_next_game_lines(self):
        return "NextGameLines"

    def get_team_fee_progress(self):
        return "TeamFeeProgress"






