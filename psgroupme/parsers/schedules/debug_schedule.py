from schedule import Schedule
from game import Game
import datetime


class DebugSchedule(Schedule):

    def __init__(self, *args, **kwargs):
        # super(DebugSchedule, self).__init__(*args, **kwargs)
        self.now = datetime.datetime.now()
        self.games = self.parse_table()
        self.refresh_count = 0

    def refresh_schedule(self):
        self.refresh_count += 1

    def parse_table(self):
        games = list()
        game_dts = [
            [self.now - datetime.timedelta(days=366), 3, 2],  # Last Year
            [self.now - datetime.timedelta(days=1), 3, 2],  # Yesterday
            [self.now + datetime.timedelta(hours=1), None, None],  # Today
            [self.now + datetime.timedelta(days=1), None, None],  # Tommorrow
            [self.now + datetime.timedelta(days=366), None, None],  # Next Year
        ]
        for game_dt in game_dts:
            game = Game(game_dt[0].strftime("%a %b %d"),
                        game_dt[0].strftime("%I:%M %p EST"),
                        'home', game_dt[1],
                        'away', game_dt[2],
                        year=game_dt[0].strftime("%Y"),
                        prevgame=None,
                        final=False)
            games.append(game)
        return games

    def send_get_request(self, url):
        pass

    def retrieve_html_table_with_class(self, url, table_class):
        pass


class ScoreUpdateDebugSchedule(DebugSchedule):

    def refresh_schedule(self):
        self.refresh_count += 1
        if self.refresh_count % 5 != 0:
            return
        first = self.games[0]
        last = self.games[len(self.games) - 1]
        first.homescore = 10 - first.homescore if first.homescore else None
        first.awayscore = 7 - first.awayscore if first.awayscore else None
        last.homescore = 10 - last.homescore if last.homescore else None
        last.awayscore = 7 - last.awayscore if last.awayscore else None


class GameFinalizedDebugSchedule(DebugSchedule):

    def refresh_schedule(self):
        self.refresh_count += 1
        if self.refresh_count % 5 != 0:
            return
        game = self.games[0]
        game.final = True


class TimeUpdateDebugSchedule(DebugSchedule):

    def refresh_schedule(self):
        self.refresh_count += 1
        if self.refresh_count % 5 != 0:
            return
        first = self.games[0]
        last = self.games[len(self.games) - 1]
        new = first.full_gametime - datetime.timedelta(days=1)
        first.parse_date(new.strftime("%a %b %d"), new.strftime("%I:%M %p"),
                         first.year, first.prevgame)
        new = last.full_gametime + datetime.timedelta(hours=1)
        last.parse_date(new.strftime("%a %b %d"), new.strftime("%I:%M %p"),
                        last.year, last.prevgame)


class GameAddDebugSchedule(DebugSchedule):

    def refresh_schedule(self):
        self.refresh_count += 1
        if self.refresh_count % 5 != 0:
            return
        last = self.games[len(self.games) - 1]
        new = last.full_gametime + datetime.timedelta(hours=1)
        self.games.append(Game(new.strftime("%a %b %d"),
                               new.strftime("%I:%M %p EST"),
                               'home', None,
                               'away', None,
                               year=new.strftime("%Y"),
                               prevgame=None))


class GameRemoveDebugSchedule(DebugSchedule):

    def parse_table(self):
        games = list()
        for x in range(0, 100):
            dt = self.now + datetime.timedelta(days=1)
            game = Game(dt.strftime("%a %b %d"),
                        dt.strftime("%I:%M %p EST"),
                        'home', None,
                        'away', None,
                        year=dt.strftime("%Y"),
                        prevgame=None)
            games.append(game)
        return games

    def refresh_schedule(self):
        self.refresh_count += 1
        if self.refresh_count % 5 != 0:
            return
        if len(self.games) > 0:
            self.games = self.games[:-1]
        else:
            self.parse_table()
