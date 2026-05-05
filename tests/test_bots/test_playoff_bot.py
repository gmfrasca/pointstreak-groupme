import unittest
from unittest import mock
from psgroupme.bots.playoff_bot import PlayoffBot
import tests.psgm_mocks as psgm_mocks

class TestPlayoffBot(unittest.TestCase):

    CFG = {
        'bots': [
            {
                "class_name": "bots.PlayoffBot", 
                "bot_name": "PlayoffBot", 
                "bot_id": "0", 
                "bot_url": "/playoffbot", 
                "schedule": {
                    "type": "pointstreak", 
                    "team_id": 0, 
                    "season_id": 0
                }, 
                "stats": {
                    "type": "sportsengine", 
                    "team_id": 0, 
                    "season_id": 0
                }
            }
        ]
    }

    @mock.patch('psgroupme.bots.base_bot.BotResponseManager', return_value=psgm_mocks.BotResponseManagerMock())
    def setUp(self, mock_brm):
        self.bot = PlayoffBot(self.CFG['bots'][0])
        self.bot.schedule = psgm_mocks.MOCK_SCHEDULE_1
        self.bot.player_stats = psgm_mocks.MockPlayerStats()

    def test_get_playoff_danger_str(self):
        result = self.bot.get_playoff_danger_str()
        self.assertEqual(result, 'No players in danger of missing playoffs')

    def test_get_playoff_danger_str_with_endangered_players(self):
        # Schedule length is 2, so at -1 or less games the player can only miss 1 game
        # Goalie can only miss 0 games (-2 games with sched length 2)
        self.bot.player_stats.players['players']['Player1'].games_played = -1
        self.bot.player_stats.players['goalies']['Goalie1'].games_played = -2
        result = self.bot.get_playoff_danger_str()
        self.assertIn('Player1 can only miss 1 more games', result)
        self.assertIn('Goalie1 can only miss 0 more games', result)

    def test_get_playoff_danger_str_with_ineligible_players(self):
        # Schedule lenght is 2, so at -3 or less games the player cannot make 'half'
        self.bot.player_stats.players['players']['Player1'].games_played = -3
        self.bot.player_stats.players['goalies']['Goalie1'].games_played = -4
        result = self.bot.get_playoff_danger_str()
        self.assertNotIn('Player1', result)
        self.assertNotIn('Goalie1', result)

    @mock.patch('psgroupme.bots.playoff_bot.PlayoffBot.respond')
    def test_check_playoff_roster(self, mock_respond):
        self.bot.check_playoff_roster("test message")
        self.bot.respond.assert_called_once_with('No players in danger of missing playoffs')

    @mock.patch('psgroupme.bots.playoff_bot.PlayoffBot.respond')
    def test_check_playoff_empty_message(self, mock_respond):
        self.bot.check_playoff("")
        self.bot.respond.assert_not_called()

    @mock.patch('psgroupme.bots.playoff_bot.PlayoffBot.respond')
    def test_check_playoff_eligible_player(self, mock_respond):
        self.bot.player_stats.players['players']['Player1'].games_played = 1
        self.bot.check_playoff("Player1", "Player1")
        self.bot.respond.assert_called_once_with('Player1 is elligible for playoffs')


    @mock.patch('psgroupme.bots.playoff_bot.PlayoffBot.respond')
    def test_check_playoff_endangered_player(self, mock_respond):
        self.bot.player_stats.players['players']['Player1'].games_played = -1
        self.bot.check_playoff("Player1", "Player1")
        self.bot.respond.assert_called_once_with('Player1 is in danger of missing playoffs. They can miss 1 more games')

    @mock.patch('psgroupme.bots.playoff_bot.PlayoffBot.respond')
    @mock.patch('psgroupme.bots.playoff_bot.PlayoffBot._load_player_stats', side_effect=Exception("Test Exception"))
    def test_check_playoff_error(self, mock_exception, mock_respond):
        self.bot.player_stats.players['players']['Player1'].games_played = -1
        self.bot.check_playoff("Player1", "Player1")
        self.bot.respond.assert_called_once_with('ERROR::Test Exception')