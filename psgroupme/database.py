from team_schedule import PointstreakSchedule
import datetime
import sqlite3

DEFAULT_DB_FILE = 'psgroupme.db'
TABLES = [
    {
        'name': 'games',
        'def': ('(game_id INTEGER PRIMARY KEY, season_id int, team_id int, ' +
                'date text, time text, hometeam text, homescore text, ' +
                'awayteam text, awayscore text, notified INTEGER DEFAULT 0)')
    },
    {
        'name': 'teams',
        'def': '(team_id int, team_name text)'
    },
    {
        'name': 'seasons',
        'def': '(season_id int, season_name int, schedule_url text)'
    }
]


class PointstreakDatabase(object):

    def __init__(self, db_file=DEFAULT_DB_FILE):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        self.init_tables()

    def init_tables(self):
        for table in TABLES:
            if self.check_if_table_exists(table['name']) is False:
                self.create_new_table(table['name'], table['def'])

    def create_new_table(self, table_name, table_format):
        cmd = "CREATE TABLE {0} {1}".format(table_name, table_format)
        self.cursor.execute(cmd)
        self.save()

    def check_if_table_exists(self, table_name):
        self.cursor.execute(("SELECT name FROM sqlite_master WHERE " +
                             "type='table' and name=?"), (table_name,))
        return self.cursor.fetchone() is not None

    def team_exists(self, team_id):
        self.cursor.execute("SELECT team_id FROM teams WHERE team_id=?",
                            (team_id,))
        return self.cursor.fetchone() is not None

    def season_exists(self, season_id):
        self.cursor.execute("SELECT season_id FROM seasons WHERE season_id=?",
                            (season_id,))
        return self.cursor.fetchone() is not None

    def add_team_if_new(self, team_id, team_name='Sharknados'):
        if self.team_exists(team_id) is False:
            self.cursor.execute(('INSERT INTO teams (team_id, team_name) ' +
                                 'VALUES (?, ?)'), (team_id, team_name))
            self.save()

    def add_season_if_new(self, season_id, season_name='Fall 2017',
                          schedule_url='TODO'):
        if self.season_exists(season_id) is False:
            self.cursor.execute(('INSERT INTO seasons (season_id, ' +
                                 'season_name, schedule_url) VALUES ' +
                                 '(?, ?, ?)'),
                                (season_id, season_name, schedule_url))
            self.save()

    def set_notified(self, game_id, notified):
        notified = 1 if notified else 0
        self.cursor.execute("UPDATE games SET notified=? WHERE game_id=?",
                            (notified, game_id))
        self.save()

    def get_game(self, game_id):
        res = self.cursor.execute("SELECT * FROM games WHERE game_id=?",
                                  (game_id,))
        desc = self.cursor.description
        game = {}
        for row in res:
            i = 0
            for col in desc:
                game[col[0]] = row[i]
                i += 1
        return game

    def game_has_been_notified(self, game_id):
        self.cursor.execute("SELECT notified FROM games WHERE game_id=?",
                            (game_id,))
        res = self.cursor.fetchone()
        return res if res is None else res[0]

    def get_game_on_date(self, date, team_id, season_id):
        self.cursor.execute(("SELECT game_id FROM games WHERE date=?" +
                             "AND team_id=? AND season_id=?"),
                            (date, team_id, season_id))
        res = self.cursor.fetchone()
        return res if res is None else res[0]

    def is_game_today(self, team_id, season_id):
        return self.get_todays_game(team_id, season_id) is not None

    def get_todays_game(self, team_id, season_id):
        today = datetime.date.today().strftime("%a, %b %d")
        return self.get_game_on_date(today, team_id, season_id)

    def get_all_games(self, team_id, season_id):
        games = []
        res = self.cursor.execute("SELECT * FROM games WHERE season_id=?" +
                                  " AND team_id=?",
                                  (season_id, team_id))
        desc = self.cursor.description
        game = {}
        for row in res:
            i = 0
            for col in desc:
                game[col[0]] = row[i]
                games.append(game)
                i += 1
        return games

    def same_time(self, game1, game2):
        return (game1['date'] == game2['date'] and
                game1['time'] == game2['time'])

    def check_gametimes_unchanged(self, games_list, team_id, season_id):
        gametimes = [{'date': x.date, 'time': x.time} for x in games_list]
        db_games = self.get_all_games(team_id, season_id)
        for db_game in db_games:
            found_match = False
            for web_game in gametimes:
                if self.same_time(db_game, web_game):
                    found_match = True
                    continue
            if found_match is False:
                return False, db_game
        return True, None

    def get_game_id_for_game(self, game, team_id, season_id):

        self.cursor.execute(('SELECT game_id from games WHERE team_id=?' +
                             ' AND season_id=?' +
                             ' AND time=?' +
                             ' AND date=?'),
                            (team_id, season_id, game.time, game.date))
        res = self.cursor.fetchone()
        return res if res is None else res[0]

    def game_exists(self, game, team_id, season_id):
        return self.get_game_id_for_game(game, team_id, season_id) is not None

    def update_game(self, game, game_id, team_id, season_id):
        self.cursor.execute(("UPDATE games SET team_id=?," +
                             " season_id=?," +
                             " time=?," +
                             " date=?," +
                             " hometeam=?," +
                             " homescore=?," +
                             " awayteam=?," +
                             " awayscore=?" +
                             " WHERE game_id=?"),
                            (team_id, season_id, game.time, game.date,
                            game.hometeam, game.homescore, game.awayteam,
                            game.awayscore, game_id))
        self.save()

    def add_game_if_new(self, game, team_id, season_id):
        if self.game_exists(game, team_id, season_id):
            # Just update for scores
            game_id = self.get_game_id_for_game(game, team_id, season_id)
            self.update_game(game, game_id, team_id, season_id)
            return
        self.cursor.execute(('INSERT INTO games (team_id, season_id, date, ' +
                             'time, hometeam, homescore, awayteam, ' +
                             'awayscore) VALUES (?, ?, ?, ?, ?, ?, ?, ?)'),
                            (team_id, season_id, game.date, game.time,
                             game.hometeam, game.homescore, game.awayteam,
                             game.awayscore))
        self.save()

    def load_games(self, games_list, team_id, season_id):
        # TODO check for dupes

        for game in games_list:
            self.add_game_if_new(game, team_id, season_id)

    def load_schedule(self, sched_obj):
        team_id = sched_obj.team_id
        season_id = sched_obj.season_id
        sched_url = sched_obj.url
        self.add_team_if_new(team_id, 'Sharknados')
        self.add_season_if_new(season_id, 'Fall 2017', sched_url)
        self.load_games(sched_obj.games, team_id, season_id)

    def save(self):
        self.conn.commit()

    def disconnect(self):
        self.conn.close()


def main():
    pd = PointstreakDatabase()
    sched = PointstreakSchedule()
    pd.load_schedule(sched)
    pd.disconnect()


if __name__ == "__main__":
    main()
