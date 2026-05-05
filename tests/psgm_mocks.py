import mock
import yaml
from psgroupme.bots import BotResponseManager
from recleagueparser.schedules.pointstreak_schedule import \
    PointstreakSchedule
from recleagueparser.schedules.game import Game
from recleagueparser.schedules.schedule import Schedule
from recleagueparser.player_stats.player_stats import PlayerStats
from recleagueparser.player_stats.player import Player

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


class BotResponseManagerMock(BotResponseManager):

    def __init__(self, cfg_path=EXAMPLE_RESP_YAML):
        self.cfg_path = cfg_path


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


# Mock Player Stats
class MockPlayerStats(PlayerStats):
    def __init__(self, *args, **kwargs):
        self._logger = mock.MagicMock()
        self.html_tables = [self.get_html_table()]
        self.players = {
            'players': {
                'Player1': Player(name='Player1'),
                'Player2': Player(name='Player2'),
            },
            'goalies': {
                'Goalie1': Player(name='Goalie1'),
            }
        }

    def get_html_table(self):
        return 'TestHtmlTable'

class TeamLockerRoomMock(object):

    def get_next_game_attendance(self):
        return "NextGameAttendance"

    def get_next_game_attendees(self):
        return "NextGameAttendees"

    def get_next_game_lines(self):
        return "NextGameLines"

    def get_team_fee_progress(self):
        return "TeamFeeProgress"






