from bs4 import BeautifulSoup
from requests import get
import datetime

# **Team Info**
# *Sharknados*
# TEAM_ID = 666456
# SEASON_ID = 17455
# *DnC SportEngine*
# TEAM_ID = 2945251
# SEASON_ID = 422822
# *Sharknados SportsEngine*
# TEAM_ID = 3367048
# SEASON_ID = 481539
# *Red Hat 2 Dash*
TEAM_ID = 14998
SEASON_ID = 0
COMPANY_ID = 'dreamsports'

# Unused for now, may be useful later for run limits in Amazon Lambda
FREE_REQUESTS = 1000000
FREE_COMP_TIME = 400000  # GB secs
ALLOCATED_MEMORY = 512  # MB
ESTIMATED_RUNTIME = 10  # secs
MAX_RESPONSES = 1024 * FREE_COMP_TIME / (ESTIMATED_RUNTIME * ALLOCATED_MEMORY)
MAX_RESPONSES = FREE_REQUESTS if MAX_RESPONSES > FREE_REQUESTS else \
    MAX_RESPONSES


class Schedule(object):

    STALE_TIME = 60
    DEFAULT_COLUMNS = {}

    def __init__(self, team_id=TEAM_ID, season_id=SEASON_ID,
                 company=COMPANY_ID, columns=None, **kwargs):
        self.html_doc = None
        self.team_id = team_id
        self.season_id = season_id
        self.team_name = None
        self.games = list()
        self.columns = self.DEFAULT_COLUMNS
        if columns and isinstance(columns, dict):
            self.columns.update(columns)
        self.url = self.get_schedule_url(team_id, season_id)
        self.refresh_schedule()
        self.last_refresh = datetime.datetime.now()

    def __repr__(self):
        """Prints the list of games in order to form a schedule"""
        res = ''
        for game in self.games:
            res += '{0}\n'.format(game)
        return res

    @property
    def schedule_is_stale(self):
        if self.html_doc is None:
            return True
        now = datetime.datetime.now()
        return (now - self.last_refresh).total_seconds() > self.STALE_TIME

    @property
    def length(self):
        return len(self.games)

    @property
    def games_remaining(self):
        val = 0
        now = datetime.datetime.now()
        for game in self.games:
            if game.full_gametime > now:
                val += 1
        return val

    def get_schedule_url(self, team_id, season_id):
        raise NotImplementedError

    def get_schedule(self):
        """Get a string representation of the current schedule"""
        return str(self)

    def get_next_game_after(self, target_datetime):
        """
        Get the next game after a given time

        Args:
            target_datetime (str): The given time to check for games after

        Returns:
            the next game after :target_datetime:
        """
        for game in self.games:
            if game.full_gametime > target_datetime:
                return game
        return None

    def get_last_game_before(self, target_datetime):
        """
        Get the last game before a given time

        Args:
            target_datetime (str): The given time to check for games before

        Returns:
            the last game before :target_datetime:
        """
        last_game = None
        for game in self.games:
            last_game = game if game.full_gametime < target_datetime \
                else last_game
        return last_game

    def get_next_game(self):
        """
        Get the next game after right now

        Returns:
            the next game after right now
        """
        return self.get_next_game_after(datetime.datetime.now())

    def get_last_game(self):
        """
        Get the last game before right now

        Returns:
            the last game before right now
        """
        return self.get_last_game_before(datetime.datetime.now())

    def parse_table(self):
        raise NotImplementedError

    def refresh_schedule(self):
        """Reload the schedule from pointstreak"""
        self.html_table = self.retrieve_html_table(self.url)
        self.games = self.parse_table()

    def send_get_request(self, url):
        self.html_doc = get(url).text
        self.last_refresh = datetime.datetime.now()

    def retrieve_html_table_with_class(self, url, table_class):
        """
        Retrieve the raw html for the table on a Poinstreak Team
        Schedule webpage

        Args:
            url (str): The URL to parse a Poinstreak Schedule from

        Returns:
             a bs tbody element containing the team schedule
        """
        if self.schedule_is_stale:
            self.send_get_request(url)
        soup = BeautifulSoup(self.html_doc, 'html.parser')
        table = soup.find("table", {'class': table_class})
        if table.tbody:
            return table.tbody
        return table
