from psgroupme.team_schedule import PointstreakSchedule, Game
from psgroupme.team_schedule import main as sched_main
import unittest
import mock
import datetime
from bs4 import BeautifulSoup

THIS_YEAR = datetime.datetime.now().year

# This would get real ugly if we followed Pep8 here. Disable for this file only
# flake8: noqa
MOCK_HTML = '''
<html>
  <head>
    <title>Mock Schedule Webpage</title>
  <head>
  <body>
    <h1>Mock Schedule Webpage</h1>
    <table class="nova-stats-table">
        <tbody>
            <tr>
              <td>
                <img height="30" src="TEST.gif" width="30"/>
              </td>
              <td class='\"text-left\"'>
                <a href="players-team.html?teamid=666456&amp;seasonid=17266">home</a>
                <b> 6</b>
              </td>
              <td>
                <img height="30" src="/logos/small/league752/team666454.gif" width="30"/>
              </td>
              <td class="text-left">
                <a href="players-team.html?teamid=666454&amp;seasonid=17266">away</a>
                <b> 0</b>
              </td>
              <td class="text-center">Fri, Aug 15 </td>
              <td>8:45 pm</td>
              <td class="text-right">
                <a href="players-boxscore.html?gameid=3134292">final</a>
                <a href="gamesheet_full.html?gameid=3134292" target="_blank">
                  <img align="absmiddle" border="0" class="nova-img--auto" height="15" src="/images/playersection/gs.gif" width="15"/>
                </a>
              </td>
            </tr>
            <tr>
              <td>
                <img height="30" src="/logos/small/league752/team666456.gif" width="30"/>
              </td>
              <td class='\"text-left\"'>
                <a href="players-team.html?teamid=666456&amp;seasonid=17266">home</a>
              </td>
              <td>
                <img height="30" src="/logos/small/league752/team666454.gif" width="30"/>
              </td>
              <td class="text-left">
                <a href="players-team.html?teamid=666454&amp;seasonid=17266">away</a>
              </td>
              <td class="text-center">Fri, Aug 25 </td>
              <td>8:45 pm</td>
              <td class="text-right">
                <a href="gamesheet_full.html?gameid=3134292" target="_blank">
                  <img align="absmiddle" border="0" class="nova-img--auto" height="15" src="/images/playersection/gs.gif" width="15"/>
                </a>
              </td>
            </tr>
        </tbody>
    </table>
  </body>
 </html>
'''


def mocked_get(*args, **kwargs):
    class MockResponse(object):
        def __init__(self, text, status_code):
            self.text = text
            self.status_code = status_code
    return MockResponse(MOCK_HTML, 200)


class TestGame(unittest.TestCase):

    def setUp(self):
        with mock.patch('psgroupme.team_schedule.datetime.datetime') as mck_dt:
            # TODO mock now instead of using real time (i.e. get this to work)
            date_str = '{0}-08-31 18:22:24.033246'.format(THIS_YEAR)
            mock_now = datetime.datetime.strptime(date_str,
                                                  '%Y-%m-%d %H:%M:%S.%f')
            mck_dt.now.return_value = mock_now
            mck_dt.side_effect = lambda *args, **kw: mock_now

        self.test_date = 'Thu, Aug 31'
        self.hour_time = '7:22 PM'

        self.game = Game(self.test_date, self.hour_time, 'home', None, 'away', None, year=2017)
        self.done_game = Game(self.test_date, self.hour_time, 'home', 6, 'away', 5, year=2017)

    def tearDown(self):
        pass

    def test_assemble_full_gametime(self):
        this_year = 2017
        date = 'Wed, Aug 5'
        time = '8:45 PM'
        parsed = self.game.assemble_full_gametime(date, time, this_year)
        self.assertEqual(parsed, datetime.datetime(this_year, 8, 5, 20, 45))
        self.assertEqual(self.game.full_gametime,
                         datetime.datetime(this_year, 8, 31, 19, 22))

    def test_print(self):
        date_str = 'Thu Aug 31 07:22PM'
        self.assertEqual(str(self.game),
                         "home vs away at {0}".format(date_str))
        self.assertEqual(str(self.done_game),
                         "home 6 : away 5 on {0}".format(date_str))


class TestPointstreakSchedule(unittest.TestCase):

    @mock.patch('psgroupme.team_schedule.get', side_effect=mocked_get)
    def setUp(self, mocked_resp):
        with mock.patch('psgroupme.team_schedule.datetime.datetime') as mck_dt:
            # TODO mock now instead of using real time (i.e. get this to work)
            date_str = '{0}-08-31 18:22:24.033246'.format(THIS_YEAR)
            mock_now = datetime.datetime.strptime(date_str,
                                                  '%Y-%m-%d %H:%M:%S.%f')
            mck_dt.now.return_value = mock_now
            mck_dt.side_effect = lambda *args, **kw: mock_now

        self.mock_now = datetime.datetime.strptime(
            '{0}-08-20 18:22:24.033246'.format(THIS_YEAR),
            '%Y-%m-%d %H:%M:%S.%f')
        self.mock_preseason = datetime.datetime.strptime(
            '{0}-07-20 18:22:24.033246'.format(THIS_YEAR),
            '%Y-%m-%d %H:%M:%S.%f')
        self.mock_postseason = datetime.datetime.strptime(
            '{0}-09-20 18:22:24.033246'.format(THIS_YEAR),
            '%Y-%m-%d %H:%M:%S.%f')
        test_date = 'Thu, Aug 31'
        test_time = '6:22 PM'
        hour_before = '5:22 PM'
        hour_after = '7:22 PM'

        self.game_in_an_hour = Game(test_date, hour_after, 'home', None, 'away', None)
        self.game_hour_ago = Game(test_date, hour_before, 'home', 6, 'away', 5)
        self.unplayed_game = Game(test_date, hour_before, 'home', None, 'away', None)

        self.schedule = PointstreakSchedule()
        self.schedule.refresh_schedule = mock.MagicMock()

    def tearDown(self):
        pass

    @mock.patch('psgroupme.team_schedule.get', side_effect=mocked_get)
    def test_retrieve_html_table(self, mocked_resp):
        tbody = self.schedule.retrieve_html_table('http://fakeurl.com')
        mocked_resp.assert_called_once()
        self.assertIsNotNone(tbody)
        self.assertIsNotNone(tbody.tr)
        self.assertIsNotNone(tbody.tr.td)
        self.assertIsNotNone(tbody.tr.td.img)
        self.assertEqual(tbody.tr.td.img['src'], 'TEST.gif')

    def test_parse_table(self):
        games = self.schedule.parse_table()
        self.assertEqual(len(games), 2)
        self.assertEqual(games[0].date, 'Fri, Aug 15')
        self.assertEqual(games[1].date, 'Fri, Aug 25')

    def test_parse_team(self):
        test_html_score = '''<html>
  <body>
    <table>
      <tr>
        <td class='\"text-left\"'>
          <a href="players-team.html?teamid=666456&amp;seasonid=17266">home</a>
          <b> 6</b>
        </td>
      </tr>
    </table>
  </body>
 </html>'''
        test_html_no_score = '''<html>
  <body>
    <table>
      <tr>
        <td class='\"text-left\"'>
          <a href="players-team.html?teamid=666456&amp;seasonid=17266">away</a>
        </td>
      </tr>
    </table>
  </body>
 </html>'''
        team_score_soup = BeautifulSoup(test_html_score,
                                        'html.parser').body.table.tr.td
        team_no_score_soup = BeautifulSoup(test_html_no_score,
                                           'html.parser').body.table.tr.td

        team, score = self.schedule.parse_team(team_score_soup)
        self.assertEqual(team, 'home')
        self.assertEqual(score, '6')

        team, score = self.schedule.parse_team(team_no_score_soup)
        self.assertEqual(team, 'away')
        self.assertEqual(score, None)

    def test_repr(self):
        expected = '''home 6 : away 0 on \w\w\w Aug 15 08:45PM
home vs away at \w\w\w Aug 25 08:45PM
'''
        print(str(self.schedule))
        self.assertRegexpMatches(str(self.schedule), expected)

    @mock.patch('psgroupme.team_schedule.datetime')
    def test_get_last_game(self, mock_datetime):
        mock_datetime.datetime = mock.MagicMock()
        mock_datetime.datetime.now = mock.MagicMock()
        mock_datetime.datetime.now.return_value = self.mock_now
        last_game = self.schedule.get_last_game()
        self.assertEqual(last_game.date, 'Fri, Aug 15')
        self.assertEqual(last_game.time, '8:45 pm')
        self.assertGreater(self.mock_now, last_game.full_gametime)
        self.assertEqual(last_game.hometeam, 'home')
        self.assertEqual(last_game.awayteam, 'away')
        self.assertEqual(last_game.homescore, '6')
        self.assertEqual(last_game.awayscore, '0')

    def test_last_game_before(self):
        last_game = self.schedule.get_last_game_before(self.mock_now)
        self.assertRegexpMatches(last_game.date, '\w\w\w, Aug 15')
        self.assertEqual(last_game.time, '8:45 pm')
        self.assertGreater(self.mock_now, last_game.full_gametime)
        self.assertEqual(last_game.hometeam, 'home')
        self.assertEqual(last_game.awayteam, 'away')
        self.assertEqual(last_game.homescore, '6')
        self.assertEqual(last_game.awayscore, '0')

    @mock.patch('psgroupme.team_schedule.datetime')
    def test_get_next_game(self, mock_datetime):
        mock_datetime.datetime = mock.MagicMock()
        mock_datetime.datetime.now = mock.MagicMock()
        mock_datetime.datetime.now.return_value = self.mock_now
        next_game = self.schedule.get_next_game()
        self.assertLess(self.mock_now, next_game.full_gametime)
        self.assertEqual(next_game.date, 'Fri, Aug 25')
        self.assertEqual(next_game.time, '8:45 pm')
        self.assertEqual(next_game.hometeam, 'home')
        self.assertEqual(next_game.awayteam, 'away')
        self.assertIsNone(next_game.homescore)
        self.assertIsNone(next_game.awayscore)

    def test_get_next_game_after(self):
        next_game = self.schedule.get_next_game_after(self.mock_now)
        self.assertLess(self.mock_now, next_game.full_gametime)
        self.assertEqual(next_game.date, "Fri, Aug 25")
        self.assertEqual(next_game.time, '8:45 pm')
        self.assertEqual(next_game.hometeam, 'home')
        self.assertEqual(next_game.awayteam, 'away')
        self.assertIsNone(next_game.homescore)
        self.assertIsNone(next_game.awayscore)

    @mock.patch('psgroupme.team_schedule.PointstreakSchedule')
    def test_main(self, mock_sched):
        mock_sched.return_code = self.schedule
        sched_main(schedule_type='pointstreak')
