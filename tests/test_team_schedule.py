from psgroupme.team_schedule import PointstreakSchedule, PointstreakGame
import unittest
import mock
import datetime


class TestPointstreakGame(unittest.TestCase):


    def setUp(self):
        with mock.patch('psgroupme.team_schedule.datetime.datetime') as mck_dt:
            # TODO mock now instead of using real time (i.e. get this to work)
            mock_now = datetime.datetime.strptime('2017-08-31 18:22:24.033246',
                                                   '%Y-%m-%d %H:%M:%S.%f')
            mck_dt.now.return_value = mock_now
            mck_dt.side_effect = lambda *args, **kw: mock_now

        self.test_date = 'Thu, Aug 31'
        self.hour_time = '7:22 PM'

        self.game = PointstreakGame(self.test_date, self.hour_time,
                                    'home', None, 'away', None)
        self.done_game = PointstreakGame(self.test_date, self.hour_time,
                                         'home', 6, 'away', 5)

    def tearDown(self):
        pass

    def test_assemble_full_gametime(self):
        this_year = datetime.datetime.now().year
        date = 'Wed, Aug 5'
        time = '8:45 PM'
        parsed = self.game.assemble_full_gametime(date, time)
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

    def setUp(self):
        with mock.patch('psgroupme.team_schedule.datetime.datetime') as mck_dt:
            # TODO mock now instead of using real time (i.e. get this to work)
            mock_now = datetime.datetime.strptime('2017-08-31 18:22:24.033246',
                                                   '%Y-%m-%d %H:%M:%S.%f')
            mck_dt.now.return_value = mock_now
            mck_dt.side_effect = lambda *args, **kw: mock_now

        test_date = 'Thu, Aug 31'
        test_time = '6:22 PM'
        hour_before = '5:22 PM'
        hour_after = '7:22 PM'

        self.game_in_an_hour = PointstreakGame(test_date, hour_after,
                                               'home', None, 'away', None)
        self.game_hour_ago = PointstreakGame(test_date, hour_before,
                                             'home', 6, 'away', 5)
        self.unplayed_game = PointstreakGame(test_date, hour_before,
                                             'home', None, 'away', None)

    def tearDown(self):
        pass
